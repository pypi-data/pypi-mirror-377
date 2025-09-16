from pydantic_settings import BaseSettings
from pydantic import Field
from urllib.parse import quote


class Settings(BaseSettings):
    DATABASE_DRIVER: str = ''
    DATABASE_USER_: str = Field(alias='DATABASE_USER', default='')
    DATABASE_USER_DOMAIN: str = ''
    DATABASE_PASSWORD: str = ''
    DATABASE_HOST: str = ''
    DATABASE_PORT: str = ''
    DATABASE_NAME: str = ''
    VERSION_TABLE: str = ''

    SOURCE: str = ''
    BATCH_MODE: bool = False
    VERBOSITY: int = 0
    EDITOR: str = ''
    POST_CREATE_COMMAND: str = ''
    PREFIX: str = ''

    @property
    def DATABASE_USER(self) -> str:
        if self.DATABASE_USER_DOMAIN:
            return f'{self.DATABASE_USER_DOMAIN}\\{self.DATABASE_USER_}'
        return self.DATABASE_USER_

    @property
    def DATABASE(self) -> str:
        return (
            f'{self.DATABASE_DRIVER}://{self.DATABASE_USER}'
            f"{':' if self.DATABASE_PASSWORD else ''}"
            f'{quote(self.DATABASE_PASSWORD)}' 
            f'@{self.DATABASE_HOST}'
            f"{':' if self.DATABASE_PORT else ''}{self.DATABASE_PORT}"
            f'/{self.DATABASE_NAME}'
        )

    @property
    def sources_list(self) -> list[str]:
        return self.SOURCE.split()

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'
