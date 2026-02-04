from enum import StrEnum

class AuthErrorCode(StrEnum):
    # === Общие ошибки аутентификации ===
    INVALID_CREDENTIALS = "invalid_credentials"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_NOT_VERIFIED = "account_not_verified"
    SESSION_EXPIRED = "session_expired"

    # === Ошибки email ===
    EMAIL_INVALID_FORMAT = "email_invalid_format"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    EMAIL_NOT_FOUND = "email_not_found"
    EMAIL_DOMAIN_BLOCKED = "email_domain_blocked"

    # === Ошибки пароля ===
    PASSWORD_TOO_SHORT = "password_too_short"
    PASSWORD_TOO_LONG = "password_too_long"
    PASSWORD_MISSING_UPPERCASE = "password_missing_uppercase"
    PASSWORD_MISSING_LOWERCASE = "password_missing_lowercase"
    PASSWORD_MISSING_DIGIT = "password_missing_digit"
    PASSWORD_NOT_MATCH_REPEAT= "password_not_match_repeat"
    PASSWORD_INCORRECT = "password_incorrect"
    PASSWORD_RESET_TOKEN_INVALID = "password_reset_token_invalid"
    PASSWORD_RESET_TOKEN_EXPIRED = "password_reset_token_expired"

    # === Ошибки JWT / токенов ===
    TOKEN_INVALID = "token_invalid"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_MISSING = "token_missing"
    TOKEN_TYPE_UNSUPPORTED = "token_type_unsupported"
    REFRESH_TOKEN_INVALID = "refresh_token_invalid"
    REFRESH_TOKEN_EXPIRED = "refresh_token_expired"
    REFRESH_TOKEN_REVOKED = "refresh_token_revoked"

    # === OAuth2: Discord ===
    DISCORD_OAUTH_FAILED = "discord_oauth_failed"
    DISCORD_INVALID_STATE = "discord_invalid_state"
    DISCORD_MISSING_SCOPE = "discord_missing_scope"
    DISCORD_ACCOUNT_NOT_LINKED = "discord_account_not_linked"
    DISCORD_API_ERROR = "discord_api_error"

    # === Прочие ===
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CAPTCHA_REQUIRED = "captcha_required"
    INVALID_REQUEST = "invalid_request"
    USER_NOT_FOUND = "user_not_found"