from pydantic_settings import BaseSettings
import tempfile


class Settings(BaseSettings):
    app_context: str = "/context"
    app_open_api_url: str = "/openapi.json"
    app_json_logs: bool = True

    # db settings start
    app_db_migration_enabled: bool = True
    app_db_migration_mode: str = "apply"
    app_db_enabled: bool = True
    app_db_host: str = "localhost"
    app_db_port: str = "5432"
    app_db_database: str = "myuser"
    app_db_user: str = "myuser"
    app_db_password: str = "superpassword"
    app_db_min_con: int = 5
    app_db_max_con: int = 20
    app_db_log_sql: bool = False
    # db settings end

    # rabbit mq broker settings start
    app_rabbit_mq_host: str = "localhost"
    app_rabbit_mq_port: int = 5672
    app_rabbit_mq_vhost: str = ""
    app_rabbit_mq_username: str = "guest"
    app_rabbit_mq_password: str = "guest"
    # durable True will retain message after rabbit mq broker restart
    app_rabbit_mq_durable: bool = False
    # passive False will create queue, exchanges and bindings during application start up
    app_rabbit_mq_passive: bool = False
    app_rabbit_mq_connect: bool = True
    app_rabbit_mq_max_retries: int = 1
    # rabbit mq broker settings end

    # rabbit mq queue/exchange settings end
    app_rabbit_inbound_queue: str = "in-bound-queue"
    app_rabbit_inbound_concurrency: int = 10
    app_rabbit_inbound_exchange: str = "in-bound-ex"
    app_rabbit_inbound_routing_key: str = "in-bound-rk"

    app_rabbit_inbound_retry_queue: str = "in-bound-retry-queue"
    app_rabbit_inbound_retry_exchange: str = "in-bound-retry-ex"
    app_rabbit_inbound_retry_routing_key: str = "in-bound-retry-rk"

    app_rabbit_outbound_queue: str = "out-bound-queue"
    app_rabbit_outbound_exchange: str = "out-bound-ex"
    app_rabbit_outbound_routing_key: str = "out-bound-rk"
    # rabbit mq queue/exchange settings end

    app_external_faq_api_base_url: str = "http://localhost:4010"
    app_file_upload_path: str = tempfile.gettempdir()

    app_include_test_routers: bool = True


settings = Settings()
