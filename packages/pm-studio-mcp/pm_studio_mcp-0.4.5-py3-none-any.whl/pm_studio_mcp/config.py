import os
from typing import Optional
"""
Constants used in the PM Studio MCP server.
"""

# =====================
# Greeting message template
# =====================
GREETING_TEMPLATE = "hello, {name}! How can I help you today? I can help you to do competitor analysis, user feedback summary, write docs and more!"

# =====================
# Configuration constants (placeholders, please update with real values as needed)
# Warning: Do not hardcode sensitive information in production code, you should consider adding environment variables in .env file.
# =====================

# Microsoft tenant ID for authentication
MICROSOFT_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"  # Microsoft tenant ID

# Titan API configuration
TITAN_CLIENT_ID = "dcca0492-ea09-452c-bf98-3750d4331d33"  # Titan API client ID
TITAN_ENDPOINT = "https://titanapi.westus2.cloudapp.azure.com/v2/query"  # Titan API endpoint
TITAN_SCOPE = "api://dcca0492-ea09-452c-bf98-3750d4331d33/signin"  # Titan API scope

# =====================
# Graph API Team Configuration
# =====================
# Microsoft Graph Client IDs mapped to team aliases
GRAPH_TEAM_MAPPING = {
    # Edge Consumer Team
    "bdb91b80-83c9-4af9-a714-3475f2ae46fe": [
        "yche",
        "gajie", 
        "juanliu",
        "mile",
        "yancheng",
        "sezho",
        "lyatin",
        "dingxiao"
    ],
    # Edge Mobile Team  
    "4661e38d-c312-40e4-8e53-c658db3d5ac7": [
        "emilywu",
        "hongjunqiu",
        "yingzhuang", 
        "lmike",
        "shengjieshi",
        "v-xiaomengli",
        "wenyuansu",
        "jinghuama"
    ],
    # SA Bill Team
    "4bef8b41-4dea-40ec-be4e-16bb0d2a0dcd": [
        "tajie",
        "xiaoxch",
        "chenxitan",
        "carmenwei",
        "liyayong",
        "v-keepliu",
        "yongweizhang"
    ],
    # SA Kelly Team
    "c94ac1df-c563-44cc-af4b-63e9547ce057": [
        "yugon",
        "danliu",
        "eviema",
        "angliu",
        "menghuihu",
        "emmaxu",
        "zhangjingwei"
    ],
    # WebComFun Team
    "533f8390-6e30-40db-8804-9b665b283876": [
        "michachen",
        "chfen",
        "alexyuan",
        "lingyanzhao",
        "nanyin",
        "siyangliu",
        "yazhouzhou",
        "yuansam", 
        "shleun"
    ]
}

# Reddit API configuration
# Reddit API client ID
REDDIT_CLIENT_ID = ""
# Reddit API client secret
REDDIT_CLIENT_SECRET = ""

# Data.ai API configuration
# Data.ai API key
DATA_AI_API_KEY = ""

# Unwrap API configuration
# Unwrap API access token
UNWRAP_ACCESS_TOKEN = ""  

# Path of your working directory, this is used to store output files
WORKING_PATH = ""

# GitHub Copilot token, should be set as an environment variable for security
GITHUB_TOKEN = ""  

def get_user_graph_id() -> str:
    """
    Auto-detect Graph Client ID by mapping user alias to team configuration.
    
    Returns:
        str: Graph Client ID for the user's team, or empty string if not found
    """
    # Use UserUtils to get current user alias and map to team
    try:
        from pm_studio_mcp.utils.graph.user import UserUtils
        
        user_alias = UserUtils.get_current_user_alias()
        if user_alias:
            user_alias = user_alias.strip().lower()
            print(f"Retrieved user alias: '{user_alias}'", flush=True)
            
            # Look up client ID from team mapping
            for graph_client_id, aliases in GRAPH_TEAM_MAPPING.items():
                if user_alias in aliases:
                    print(f"Found Graph Client ID: {graph_client_id[:8]}...", flush=True)
                    return graph_client_id
            
            print(f"User alias '{user_alias}' not found in team mapping", flush=True)
            
    except Exception as e:
        print(f"UserUtils failed: {e}", flush=True)
    
    print("No Graph Client ID found", flush=True)
    return ""

class Config:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._initialize_config()

    def _initialize_config(self):

        # Greeting message configuration
        self.GREETING_TEMPLATE = os.environ.get('GREETING_TEMPLATE', GREETING_TEMPLATE)

        # Working directory configuration
        self.WORKING_PATH = os.environ.get('WORKING_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../temp'))
        os.makedirs(self.WORKING_PATH, exist_ok=True)

        # Reddit API configuration
        self.REDDIT_CLIENT_ID = self._get_config_value('REDDIT_CLIENT_ID', REDDIT_CLIENT_ID)
        self.REDDIT_CLIENT_SECRET = self._get_config_value('REDDIT_CLIENT_SECRET', REDDIT_CLIENT_SECRET)

        # Data.ai API configuration
        self.DATA_AI_API_KEY = self._get_config_value('DATA_AI_API_KEY', DATA_AI_API_KEY)

        # Microsoft Graph API configuration
        self.GRAPH_CLIENT_ID = self._get_config_value('GRAPH_CLIENT_ID', get_user_graph_id()) 

        # Microsoft authentication configuration
        self.MICROSOFT_TENANT_ID = self._get_config_value('MICROSOFT_TENANT_ID', MICROSOFT_TENANT_ID)

        # Unwrap API configuration
        self.UNWRAP_ACCESS_TOKEN = self._get_config_value('UNWRAP_ACCESS_TOKEN', UNWRAP_ACCESS_TOKEN) 

        # Titan API configuration
        self.TITAN_CLIENT_ID = self._get_config_value('TITAN_CLIENT_ID', TITAN_CLIENT_ID)
        self.TITAN_ENDPOINT = self._get_config_value('TITAN_ENDPOINT',  TITAN_ENDPOINT)
        self.TITAN_SCOPE = self._get_config_value('TITAN_SCOPE', TITAN_SCOPE)

        # Google Ads API configuration
        self.GOOGLE_ADS_DEVELOPER_TOKEN = self._get_config_value('GOOGLE_ADS_DEVELOPER_TOKEN', '')
        self.GOOGLE_ADS_LOGIN_CUSTOMER_ID = self._get_config_value('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
        self.GOOGLE_ADS_CLIENT_SECRET_JSON = self._get_config_value('GOOGLE_ADS_CLIENT_SECRET_JSON', '')
        self.GOOGLE_ADS_CREDENTIALS_JSON = self._get_config_value('GOOGLE_ADS_CREDENTIALS_JSON', '')

        # GitHub Copilot configuration
        # Note: GitHub Copilot token should be set as an environment variable for security
        self.GITHUB_TOKEN = self._get_config_value('GITHUB_TOKEN', GITHUB_TOKEN)

    def _get_config_value(self, env_var: str, default_value: str) -> str:
        value = os.environ.get(env_var)
        if value:
            print(f"Using {env_var} from environment")
            return value
        print(f"Using default value for {env_var}")
        return default_value

# Create global config instance
config = Config()