from src.infdb.InfdbConfig import InfdbConfig
from src.infdb.InfdbClient import InfdbClient
from src.infdb.InfdbLogger import InfdbLogger
import logging

class InfDB:
    """Responsible for handling logging and connections to InfDB database."""

    
    def __init__(self, tool_name, config_path="configs"):
        self.tool_name = tool_name
        self.config_path = config_path 

        # Load InfDB configuration
        self.infdbconfig = InfdbConfig(tool_name=self.tool_name, config_path=self.config_path)

        # Initialize logging
        self.infdblogger = InfdbLogger(self.infdbconfig)

    
    def __str__(self):
        return f"Infdb connected to {self.infdbclient.db_params} using config {self.infdbconfig}"
    
    
    def get_log(self):
        """Get the root logger."""
        return self.infdblogger.root_logger
    
    def get_worker_logger(self):
        """Get the worker logger for multiprocessing."""
        return self.infdblogger.setup_worker_logger()
    
    
    def connect(self, db_name="citydb"):
        """Establish a connection to the InfDB database."""
        infdbclient = InfdbClient(self.infdbconfig, db_name=db_name)
        self.log.debug(f"InfDB client connected: {infdbclient}")
        return infdbclient
    

    def get_toolname(self):
        """Get the tool name."""
        return self.tool_name
    

    def get_config_dict(self):
        """Get the loaded configuration as dictionary."""
        return self.infdbconfig    
    

    def get_config_value(self, keys):
        """Get a specific configuration value."""
        return self.infdbconfig.get_value(keys)
    
    
    def get_config_path(self, keys):
        """Get a specific configuration value as path."""
        return self.infdbconfig.get_path(keys)


    def get_tool_config_value(self, keys):
        """Get the configuration section for the current tool."""
        return self.infdbconfig.get_value([self.tool_name, keys])
    
    
    def get_tool_config_path(self, keys):
        """Get the configuration section for the current tool as path."""
        return self.infdbconfig.get_path([self.tool_name, keys])