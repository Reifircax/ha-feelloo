"""Constants for the Feelloo integration."""

from datetime import timedelta

DOMAIN = "feelloo"

# Firebase Auth
FIREBASE_API_KEY = "AIzaSyDuAHqBZTwfri9qC0rhayRv_7VdQCTF8co"
FIREBASE_SIGNIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIREBASE_REFRESH_URL = "https://securetoken.googleapis.com/v1/token"

# Feelloo API
BASE_URL = "https://linxmain.feelloo.com"

# Config entry keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Configurable polling intervals (minutes, between 1 min and 24 h via options flow)
CONF_CATS_UPDATE_INTERVAL = "cats_update_interval"
CONF_ACTIVITY_UPDATE_INTERVAL = "activity_update_interval"
CONF_ACTIVITY_WEEK_UPDATE_INTERVAL = "activity_week_update_interval"
CONF_ACTIVITY_MONTH_UPDATE_INTERVAL = "activity_month_update_interval"
CONF_TERRITORY_UPDATE_INTERVAL = "territory_update_interval"
CONF_SESSION_UPDATE_INTERVAL = "session_update_interval"

# Default update intervals (minutes)
DEFAULT_CATS_UPDATE_INTERVAL = 5
DEFAULT_ACTIVITY_UPDATE_INTERVAL = 15
DEFAULT_ACTIVITY_WEEK_UPDATE_INTERVAL = 60
DEFAULT_ACTIVITY_MONTH_UPDATE_INTERVAL = 360
DEFAULT_TERRITORY_UPDATE_INTERVAL = 15
DEFAULT_SESSION_UPDATE_INTERVAL = 30

# Enable/disable flags for the configurable polling intervals
# (the cats / GPS polling is always active and has no flag)
CONF_ACTIVITY_ENABLED = "activity_enabled"
CONF_ACTIVITY_WEEK_ENABLED = "activity_week_enabled"
CONF_ACTIVITY_MONTH_ENABLED = "activity_month_enabled"
CONF_TERRITORY_ENABLED = "territory_enabled"
CONF_SESSION_ENABLED = "session_enabled"

# Default enabled states
DEFAULT_ACTIVITY_ENABLED = True
DEFAULT_ACTIVITY_WEEK_ENABLED = True
DEFAULT_ACTIVITY_MONTH_ENABLED = True
DEFAULT_TERRITORY_ENABLED = True
DEFAULT_SESSION_ENABLED = True

# Allowed range for user-configurable update intervals (minutes)
MIN_UPDATE_INTERVAL_MINUTES = 1
MAX_UPDATE_INTERVAL_MINUTES = 1440  # 24h

# Fixed intervals (not user-configurable)
TOKEN_REFRESH_INTERVAL = timedelta(minutes=50)
FAST_POLLING_INTERVAL = timedelta(minutes=1)

# API endpoints
ENDPOINT_CATS = "/users/cats"
ENDPOINT_CAT_DETAIL = "/users/cats/{cat_id}"
ENDPOINT_ACTIVITY = "/users/cats/{cat_id}/activity"
ENDPOINT_TERRITORY_PATHS = "/users/cats/{cat_id}/territory/paths"
ENDPOINT_TERRITORY_PATH = "/users/cats/{cat_id}/territory/paths/{session_id}"
ENDPOINT_TERRITORY = "/users/cats/{cat_id}/territory"
ENDPOINT_RING = "/users/cats/{cat_id}/ring/bell-button"
ENDPOINT_PETITE_SOURIS = "/users/cats/{cat_id}/territory/petite-souris-button"
