import asyncio
import logging
from typing import Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import *
from .core.entity_parser import EntityParser
from .core.model_generator import ModelGenerator
from .db.connection import DatabaseManager, set_db_manager
from .security.auth import AuthManager
from .api.crud_generator import CRUDGenerator
from .api.auth_routes import router as auth_router

# Configurar logging
if LOG:
    logging.basicConfig(
        level=logging.INFO if DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

class BackendGenerator:
    """Generador principal del backend"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Backend Generador",
            description="Backend generado automáticamente desde archivos YAML",
            version="1.0.0",
            debug=DEBUG
        )
        
        # Configurar CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Inicializar componentes
        # EntityParser se inicializará después de aplicar configuración personalizada
        self.entity_parser = None
        self.model_generator = ModelGenerator()
        # DatabaseManager se inicializará después de aplicar configuración personalizada
        self.db_manager = None
        self.auth_manager = AuthManager(
            secret_key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
            access_token_expire_minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.crud_generator = CRUDGenerator(self.auth_manager)
        
        # Modelos generados
        self.generated_models = {}
        self.pydantic_models = {}
        
    async def initialize(self):
        """Inicializa el backend completo"""
        try:
            logger.info("Iniciando generación del backend...")
            
            # 0. Inicializar DatabaseManager con configuración actualizada
            from .config import DATABASE_URL
            self.db_manager = DatabaseManager(DATABASE_URL)
            logger.info(f"DatabaseManager inicializado con URL: {DATABASE_URL}")
            
            # 0.5. Inicializar EntityParser con configuración actualizada
            from .config import ENTITIES_PATH
            self.entity_parser = EntityParser(ENTITIES_PATH)
            logger.info(f"EntityParser inicializado con ruta: {ENTITIES_PATH}")
            
            # 1. Cargar entidades desde YAML
            logger.info("Cargando entidades desde archivos YAML...")
            entities = self.entity_parser.load_entities()
            
            if not entities:
                logger.warning("No se encontraron entidades para cargar")
                return
                
            # 2. Generar modelos ORM y Pydantic
            logger.info("Generando modelos ORM y Pydantic...")
            models_result = self.model_generator.generate_all_models(entities)
            self.generated_models = models_result['orm_models']
            self.pydantic_models = models_result['pydantic_models']
            
            # 3. Inicializar base de datos
            logger.info("Inicializando base de datos...")
            all_models = list(self.generated_models.values())
            
            if INSTALL:
                logger.info("Modo instalación activado - reiniciando base de datos...")
                await self.db_manager.init_db(all_models)
                await self.db_manager.reset_db()
                await self._create_initial_users()
            else:
                await self.db_manager.init_db(all_models)
            
            # Establecer DatabaseManager global
            set_db_manager(self.db_manager)
            
            # 4. Generar endpoints CRUD
            logger.info("Generando endpoints CRUD...")
            for entity_name, entity_data in entities.items():
                if entity_name in self.generated_models and entity_name in self.pydantic_models:
                    model_class = self.generated_models[entity_name]
                    pydantic_models = self.pydantic_models[entity_name]
                    
                    router = self.crud_generator.generate_crud_router(
                        entity_name=entity_name,
                        entity_data=entity_data,
                        model_class=model_class,
                        pydantic_models=pydantic_models
                    )
                    
                    # Registrar router
                    self.app.include_router(router)
                    logger.info(f"Router generado para entidad: {entity_name}")
            
            # 5. Registrar rutas de autenticación
            self.app.include_router(auth_router)
            
            # 6. Registrar rutas personalizadas
            from .config import CUSTOM_ROUTES
            if CUSTOM_ROUTES:
                logger.info("Registrando rutas personalizadas...")
                for route in CUSTOM_ROUTES:
                    self._register_custom_route(route)
                    logger.info(f"Ruta personalizada registrada: {route['metodo']} {route['path']}")
            
            # 7. Endpoint de salud
            @self.app.get("/")
            async def health_check():
                return {
                    "status": "ok",
                    "message": "Backend funcionando correctamente"
                }
            
            logger.info("Backend generado exitosamente!")
            
        except Exception as e:
            logger.error(f"Error durante la inicialización: {e}")
            raise
    
    def _register_custom_route(self, route):
        """Registra una ruta personalizada"""
        path = route['path']
        method = route['metodo'].upper()
        function = route['funcion']
        permissions = route.get('permisos', [])
        
        # Crear endpoint con permisos
        if permissions:
            endpoint_func = self._create_protected_endpoint(function, permissions)
        else:
            endpoint_func = self._create_public_endpoint(function)
        
        # Registrar la ruta según el método HTTP
        if method == 'GET':
            self.app.get(path)(endpoint_func)
        elif method == 'POST':
            self.app.post(path)(endpoint_func)
        elif method == 'PUT':
            self.app.put(path)(endpoint_func)
        elif method == 'DELETE':
            self.app.delete(path)(endpoint_func)
    
    def _create_public_endpoint(self, original_func):
        """Crea un endpoint público"""
        import inspect
        
        async def endpoint_wrapper(request: Request):
            try:
                logger.info(f"Endpoint público llamado: {original_func.__name__}")
                
                # Verificar si la función espera parámetros
                sig = inspect.signature(original_func)
                if len(sig.parameters) == 0:
                    # Función sin parámetros
                    result = original_func()
                else:
                    # Función con parámetros - extraer parámetros de la request
                    try:
                        # Obtener parámetros de la URL path
                        path_params = request.path_params
                        
                        # Obtener parámetros del body si es POST/PUT
                        body_params = {}
                        if request.method in ['POST', 'PUT']:
                            try:
                                body_params = await request.json()
                            except:
                                pass
                        
                        # Combinar parámetros
                        func_params = {}
                        for param_name, param_info in sig.parameters.items():
                            if param_name in path_params:
                                # Parámetro de la URL
                                func_params[param_name] = path_params[param_name]
                            elif param_name in body_params:
                                # Parámetro del body
                                func_params[param_name] = body_params[param_name]
                            elif param_name == 'user_data' and 'user_data' in body_params:
                                # Caso especial para user_data
                                func_params[param_name] = body_params['user_data']
                            elif param_name == 'x' and 'x' in body_params:
                                # Caso especial para x
                                func_params[param_name] = body_params['x']
                            elif param_name == 'y' and 'y' in body_params:
                                # Caso especial para y
                                func_params[param_name] = body_params['y']
                        
                        # Ejecutar función con parámetros
                        result = original_func(**func_params)
                    except Exception as e:
                        logger.error(f"Error procesando parámetros para {original_func.__name__}: {e}")
                        result = {"error": f"Error procesando parámetros: {str(e)}"}
                
                logger.info(f"Endpoint público {original_func.__name__} ejecutado exitosamente")
                return result
            except Exception as e:
                logger.error(f"Error en endpoint público {original_func.__name__}: {e}")
                return {"error": str(e)}
        
        return endpoint_wrapper
    
    def _create_protected_endpoint(self, original_func, permissions):
        """Crea un endpoint protegido con permisos"""
        import inspect
        from fastapi import Request, HTTPException, Depends
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        
        security = HTTPBearer()
        
        async def endpoint_wrapper(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
            try:
                logger.info(f"Endpoint protegido llamado: {original_func.__name__} por usuario con permisos: {permissions}")
                
                # Obtener usuario actual usando el AuthManager
                current_user = await self.auth_manager.get_current_user(credentials)
                
                # Verificar permisos
                user_role = getattr(current_user, 'rol', '')
                if user_role not in permissions:
                    logger.warning(f"Usuario {getattr(current_user, 'nombre', 'desconocido')} sin permisos para {original_func.__name__}")
                    raise HTTPException(status_code=403, detail="Permisos insuficientes")
                
                logger.info(f"Usuario autenticado: {getattr(current_user, 'nombre', 'desconocido')}")
                
                # Verificar si la función espera parámetros
                sig = inspect.signature(original_func)
                if len(sig.parameters) == 0:
                    # Función sin parámetros
                    result = original_func()
                else:
                    # Función con parámetros - extraer parámetros de la request
                    try:
                        # Obtener parámetros de la URL path
                        path_params = request.path_params
                        
                        # Obtener parámetros del body si es POST/PUT
                        body_params = {}
                        if request.method in ['POST', 'PUT']:
                            try:
                                body_params = await request.json()
                            except:
                                pass
                        
                        # Combinar parámetros
                        func_params = {}
                        for param_name, param_info in sig.parameters.items():
                            if param_name in path_params:
                                # Parámetro de la URL
                                func_params[param_name] = path_params[param_name]
                            elif param_name in body_params:
                                # Parámetro del body
                                func_params[param_name] = body_params[param_name]
                            elif param_name == 'user_data' and 'user_data' in body_params:
                                # Caso especial para user_data
                                func_params[param_name] = body_params['user_data']
                            elif param_name == 'x' and 'x' in body_params:
                                # Caso especial para x
                                func_params[param_name] = body_params['x']
                            elif param_name == 'y' and 'y' in body_params:
                                # Caso especial para y
                                func_params[param_name] = body_params['y']
                        
                        # Ejecutar función con parámetros
                        result = original_func(**func_params)
                    except Exception as e:
                        logger.error(f"Error procesando parámetros para {original_func.__name__}: {e}")
                        result = {"error": f"Error procesando parámetros: {str(e)}"}
                
                logger.info(f"Endpoint protegido {original_func.__name__} ejecutado exitosamente por {user_role}")
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error en endpoint protegido {original_func.__name__}: {e}")
                return {"error": str(e)}
        
        return endpoint_wrapper
    
    async def _create_initial_users(self):
        """Crea usuarios iniciales para modo instalación"""
        try:
            # Obtener el modelo Usuario desde los modelos generados
            from .config import AUTH, INITIAL_USERS
            from sqlalchemy import select
            
            # Obtener el modelo Usuario desde los modelos generados
            Usuario = self.generated_models.get('Usuario')
            if not Usuario:
                logger.warning("Modelo Usuario no encontrado, saltando creación de usuarios iniciales")
                return
            
            # Obtener la columna de usuario desde la configuración
            user_column = AUTH['columna_usuario']
            password_column = AUTH['columna_password']
            
            async with self.db_manager.get_session() as session:
                for user_data in INITIAL_USERS:
                    # Verificar si el usuario ya existe usando la columna configurada
                    result = await session.execute(
                        select(Usuario).where(getattr(Usuario, user_column) == user_data[user_column])
                    )
                    existing_user = result.scalar_one_or_none()
                    
                    if not existing_user:
                        # Crear hash de la contraseña
                        hashed_password = self.auth_manager.get_password_hash(user_data[password_column])
                        
                        # Crear usuario usando las columnas configuradas
                        user_kwargs = {
                            user_column: user_data[user_column],
                            password_column: hashed_password,
                            'rol': user_data['rol']
                        }
                        
                        # Agregar campos adicionales si existen
                        for key, value in user_data.items():
                            if key not in [user_column, password_column, 'rol']:
                                user_kwargs[key] = value
                        
                        new_user = Usuario(**user_kwargs)
                        session.add(new_user)
                        await session.commit()
                        logger.info(f"Usuario inicial creado: {user_data[user_column]}")
                    else:
                        logger.info(f"Usuario ya existe: {user_data[user_column]}")
                        
        except Exception as e:
            logger.error(f"Error creando usuarios iniciales: {e}")
            raise
    
    def run(self):
        """Ejecuta el servidor"""
        # Inicializar el backend antes de ejecutar el servidor
        asyncio.run(self.initialize())
        
        uvicorn.run(
            self.app,
            host="0.0.0.0",
            port=PORT,
            log_level="info" if DEBUG else "warning"
        )

def create_backend():
    """Función factory para crear y configurar el backend"""
    return BackendGenerator()

def run_backend():
    """Función para ejecutar el backend completo"""
    async def main():
        backend = create_backend()
        await backend.initialize()
        return backend
    
    # Ejecutar la inicialización
    backend = asyncio.run(main())
    
    # Ejecutar el servidor usando la configuración del puerto
    import uvicorn
    from .config import PORT
    
    print(f"🚀 Iniciando servidor en puerto {PORT}...")
    uvicorn.run(backend.app, host="0.0.0.0", port=PORT) 