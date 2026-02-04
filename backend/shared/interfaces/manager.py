from abc import ABC, abstractmethod

class BaseManager(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def dispose(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def health_check(self, auto_error: bool = False) -> bool:
        raise NotImplementedError
    
    # @abstractmethod
    # def checking_readiness(self) -> None:
    #     raise NotImplementedError