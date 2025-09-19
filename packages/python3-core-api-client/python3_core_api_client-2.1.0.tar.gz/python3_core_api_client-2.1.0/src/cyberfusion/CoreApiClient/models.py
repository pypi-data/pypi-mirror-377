from datetime import datetime
from enum import StrEnum, IntEnum
from ipaddress import IPv4Address, IPv6Address
from typing import Dict, List, Literal, Optional, Union, Any

from pydantic import UUID4, AnyUrl, EmailStr, Field, confloat, conint, constr, BaseModel
from typing import Iterator


class CoreApiModel(BaseModel):
    pass


class RootModelCollectionMixin:
    """Mixin supporting iterating over and accessing items in a root model, without explicitly accessing __root__.

    Inspired by https://docs.pydantic.dev/2.0/usage/models/#rootmodel-and-custom-root-types
    """

    __root__: dict | list | None

    def __iter__(self) -> Iterator:
        if not isinstance(self.__root__, (list, dict)):
            raise TypeError("Type does not support iter")

        return iter(self.__root__)

    def __getitem__(self, item: Any) -> Any:
        if not isinstance(self.__root__, (list, dict)):
            raise TypeError("Type does not support getitem")

        return self.__root__[item]

    def items(self) -> Any:
        if not isinstance(self.__root__, (dict)):
            raise TypeError("Type does not support items")

        return self.__root__.items()


class SpecificationMode(StrEnum):
    SINGLE = "Single"
    OR = "Or"


class ObjectLogTypeEnum(StrEnum):
    Create = "Create"
    Update = "Update"
    Delete = "Delete"


class CauserTypeEnum(StrEnum):
    API_User = "API User"


class HTTPMethod(StrEnum):
    CONNECT = "CONNECT"
    DELETE = "DELETE"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"


class APIUserAuthenticationMethodEnum(StrEnum):
    API_KEY = "API Key"
    JWT_TOKEN = "JWT Token"


class APIUserInfo(CoreApiModel):
    id: int
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    is_active: bool
    is_superuser: bool
    clusters: List[int] = Field(..., unique_items=True)
    customer_id: Optional[int]
    authentication_method: APIUserAuthenticationMethodEnum


class AllowOverrideDirectiveEnum(StrEnum):
    ALL = "All"
    AUTHCONFIG = "AuthConfig"
    FILEINFO = "FileInfo"
    INDEXES = "Indexes"
    LIMIT = "Limit"
    NONE = "None"


class AllowOverrideOptionDirectiveEnum(StrEnum):
    ALL = "All"
    FOLLOWSYMLINKS = "FollowSymLinks"
    INDEXES = "Indexes"
    MULTIVIEWS = "MultiViews"
    SYMLINKSIFOWNERMATCH = "SymLinksIfOwnerMatch"
    NONE = "None"


class BasicAuthenticationRealmCreateRequest(CoreApiModel):
    directory_path: Optional[str]
    virtual_host_id: int
    name: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64)
    htpasswd_file_id: int


class BasicAuthenticationRealmUpdateRequest(CoreApiModel):
    name: Optional[constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64)] = (
        None
    )
    htpasswd_file_id: Optional[int] = None


class BodyLoginAccessToken(CoreApiModel):
    grant_type: Optional[constr(regex=r"^password$")] = None
    username: str
    password: str
    scope: Optional[str] = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class BorgArchiveContentObjectTypeEnum(StrEnum):
    REGULAR_FILE = "regular_file"
    DIRECTORY = "directory"
    SYMBOLIC_LINK = "symbolic_link"


class BorgArchiveCreateDatabaseRequest(CoreApiModel):
    borg_repository_id: int
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    database_id: int


class BorgArchiveCreateUNIXUserRequest(CoreApiModel):
    borg_repository_id: int
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int


class BorgArchiveMetadata(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    borg_archive_id: int
    exists_on_server: bool
    contents_path: Optional[str]


class BorgRepositoryCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    passphrase: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    remote_host: str
    remote_path: str
    remote_username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    unix_user_id: Optional[int]
    cluster_id: int
    keep_hourly: Optional[int]
    keep_daily: Optional[int]
    keep_weekly: Optional[int]
    keep_monthly: Optional[int]
    keep_yearly: Optional[int]
    identity_file_path: Optional[str]


class BorgRepositoryUpdateRequest(CoreApiModel):
    keep_hourly: Optional[int] = None
    keep_daily: Optional[int] = None
    keep_weekly: Optional[int] = None
    keep_monthly: Optional[int] = None
    keep_yearly: Optional[int] = None
    identity_file_path: Optional[str] = None


class CMSConfigurationConstant(CoreApiModel):
    value: Union[str, int, float, bool]
    index: Optional[conint(ge=0)] = None
    name: constr(regex=r"^[a-zA-Z0-9_]+$", min_length=1)


class CMSConfigurationConstantUpdateRequest(CoreApiModel):
    value: Union[str, int, float, bool]
    index: Optional[conint(ge=0)] = None


class CMSInstallNextCloudRequest(CoreApiModel):
    database_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63)
    database_user_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63)
    database_user_password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)
    database_host: str
    admin_username: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60)
    admin_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)


class CMSInstallWordPressRequest(CoreApiModel):
    database_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63)
    database_user_name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=63)
    database_user_password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)
    database_host: str
    admin_username: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60)
    admin_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    site_title: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=253)
    site_url: AnyUrl
    locale: constr(regex=r"^[a-zA-Z_]+$", min_length=1, max_length=15)
    version: constr(regex=r"^[0-9.]+$", min_length=1, max_length=6)
    admin_email_address: EmailStr


class CMSOneTimeLogin(CoreApiModel):
    url: AnyUrl


class CMSOptionNameEnum(StrEnum):
    BLOG_PUBLIC = "blog_public"


class CMSOptionUpdateRequest(CoreApiModel):
    value: conint(ge=0, le=1)


class CMSPlugin(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9_]+$", min_length=1)
    current_version: constr(regex=r"^[a-z0-9.-]+$", min_length=1)
    available_version: Optional[constr(regex=r"^[a-z0-9.-]+$", min_length=1)]
    is_enabled: bool


class CMSSoftwareNameEnum(StrEnum):
    WORDPRESS = "WordPress"
    NEXTCLOUD = "NextCloud"


class CMSThemeInstallFromRepositoryRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=60)
    version: Optional[constr(regex=r"^[0-9.]+$", min_length=1, max_length=6)]


class CMSThemeInstallFromURLRequest(CoreApiModel):
    url: AnyUrl


class CMSUserCredentialsUpdateRequest(CoreApiModel):
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)


class CertificateCreateRequest(CoreApiModel):
    certificate: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535
    )
    ca_chain: constr(regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535)
    private_key: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n ]+$", min_length=1, max_length=65535
    )
    cluster_id: int


class CertificateManagerUpdateRequest(CoreApiModel):
    request_callback_url: Optional[AnyUrl] = None


class CertificateProviderNameEnum(StrEnum):
    LETS_ENCRYPT = "lets_encrypt"


class ClusterBorgSSHKey(CoreApiModel):
    public_key: str


class NodejsVersion(CoreApiModel):
    __hash__ = object.__hash__

    __root__: constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")


class ClusterIPAddress(CoreApiModel):
    ip_address: Union[IPv6Address, IPv4Address]
    dns_name: Optional[str]
    l3_ddos_protection_enabled: bool


class ClusterIPAddresses(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Dict[str, List[ClusterIPAddress]]]] = None


class CronCreateRequest(CoreApiModel):
    node_id: Optional[int]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    email_address: Optional[EmailStr]
    schedule: str
    error_count: int
    random_delay_max_seconds: int
    timeout_seconds: Optional[int]
    locking_enabled: bool
    is_active: bool
    memory_limit: Optional[conint(ge=256)] = None
    cpu_limit: Optional[int] = None


class CronUpdateRequest(CoreApiModel):
    command: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)] = None
    email_address: Optional[EmailStr] = None
    schedule: Optional[str] = None
    error_count: Optional[int] = None
    random_delay_max_seconds: Optional[int] = None
    timeout_seconds: Optional[int] = None
    locking_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    memory_limit: Optional[conint(ge=256)] = None
    cpu_limit: Optional[int] = None
    node_id: Optional[int] = None


class CustomConfigServerSoftwareNameEnum(StrEnum):
    NGINX = "nginx"


class CustomConfigSnippetTemplateNameEnum(StrEnum):
    LARAVEL = "Laravel"
    COMPRESSION = "Compression"


class CustomConfigSnippetUpdateRequest(CoreApiModel):
    contents: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)] = (
        None
    )
    is_default: Optional[bool] = None


class CustomConfigUpdateRequest(CoreApiModel):
    contents: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)] = (
        None
    )


class CustomerIPAddressDatabase(CoreApiModel):
    ip_address: Union[IPv6Address, IPv4Address]
    dns_name: Optional[str]


class CustomerIPAddresses(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Dict[str, List[CustomerIPAddressDatabase]]]] = None


class CustomerIncludes(CoreApiModel):
    pass


class CustomerResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    identifier: constr(regex=r"^[a-z0-9]+$", min_length=2, max_length=4)
    dns_subdomain: str
    is_internal: bool
    team_code: constr(regex=r"^[A-Z0-9]+$", min_length=4, max_length=6)
    includes: CustomerIncludes


class DaemonCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    nodes_ids: List[int] = Field(..., min_items=1, unique_items=True)
    memory_limit: Optional[conint(ge=256)] = None
    cpu_limit: Optional[int] = None


class DaemonUpdateRequest(CoreApiModel):
    command: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)] = None
    nodes_ids: Optional[List[int]] = None
    memory_limit: Optional[conint(ge=256)] = None
    cpu_limit: Optional[int] = None


class IdenticalTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class NotIdenticalTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class OnlyLeftTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class OnlyRightTablesName(CoreApiModel):
    __root__: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)


class DatabaseComparison(CoreApiModel):
    identical_tables_names: List[IdenticalTablesName] = Field(..., unique_items=True)
    not_identical_tables_names: List[NotIdenticalTablesName] = Field(
        ..., unique_items=True
    )
    only_left_tables_names: List[OnlyLeftTablesName] = Field(..., unique_items=True)
    only_right_tables_names: List[OnlyRightTablesName] = Field(..., unique_items=True)


class DatabaseServerSoftwareNameEnum(StrEnum):
    MARIADB = "MariaDB"
    POSTGRESQL = "PostgreSQL"


class DatabaseUpdateRequest(CoreApiModel):
    optimizing_enabled: Optional[bool] = None
    backups_enabled: Optional[bool] = None


class DatabaseUsageIncludes(CoreApiModel):
    pass


class DatabaseUsageResource(CoreApiModel):
    database_id: int
    usage: confloat(ge=0.0)
    timestamp: datetime
    includes: DatabaseUsageIncludes


class DatabaseUserUpdateRequest(CoreApiModel):
    phpmyadmin_firewall_groups_ids: Optional[List[int]] = None
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = None


class DetailMessage(CoreApiModel):
    detail: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)


class DocumentRootFileSuffixEnum(StrEnum):
    PHP = "php"


class DomainRouterCategoryEnum(StrEnum):
    GRAFANA = "Grafana"
    SINGLESTORE_STUDIO = "SingleStore Studio"
    SINGLESTORE_API = "SingleStore API"
    METABASE = "Metabase"
    KIBANA = "Kibana"
    RABBITMQ_MANAGEMENT = "RabbitMQ Management"
    VIRTUAL_HOST = "Virtual Host"
    URL_REDIRECT = "URL Redirect"


class DomainRouterUpdateRequest(CoreApiModel):
    node_id: Optional[int] = None
    certificate_id: Optional[int] = None
    security_txt_policy_id: Optional[int] = None
    firewall_groups_ids: Optional[List[int]] = None
    force_ssl: Optional[bool] = None


class EncryptionTypeEnum(StrEnum):
    TLS = "TLS"
    SSL = "SSL"
    STARTTLS = "STARTTLS"


class FPMPoolCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    version: str
    unix_user_id: int
    max_children: int
    max_requests: int
    process_idle_timeout: int
    cpu_limit: Optional[int]
    log_slow_requests_threshold: Optional[int]
    is_namespaced: bool
    memory_limit: Optional[conint(ge=256)] = None


class FPMPoolUpdateRequest(CoreApiModel):
    max_children: Optional[int] = None
    max_requests: Optional[int] = None
    process_idle_timeout: Optional[int] = None
    cpu_limit: Optional[int] = None
    log_slow_requests_threshold: Optional[int] = None
    is_namespaced: Optional[bool] = None
    memory_limit: Optional[conint(ge=256)] = None


class FTPUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_.@]+$", min_length=1, max_length=32)
    unix_user_id: int
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    directory_path: str


class FTPUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = None
    directory_path: Optional[str] = None


class FirewallGroupCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9_]+$", min_length=1, max_length=32)
    cluster_id: int
    ip_networks: List[str] = Field(
        ...,
        min_items=1,
        unique_items=True,
    )


class FirewallGroupUpdateRequest(CoreApiModel):
    ip_networks: Optional[List[str]] = None


class FirewallRuleExternalProviderNameEnum(StrEnum):
    ATLASSIAN = "Atlassian"
    AWS = "AWS"
    BUDDY = "Buddy"
    GOOGLE_CLOUD = "Google Cloud"


class FirewallRuleServiceNameEnum(StrEnum):
    SSH = "SSH"
    PROFTPD = "ProFTPD"
    NGINX = "nginx"
    APACHE = "Apache"


class HAProxyListenToNodeCreateRequest(CoreApiModel):
    haproxy_listen_id: int
    node_id: int


class HTTPRetryConditionEnum(StrEnum):
    CONNECTION_FAILURE = "Connection failure"
    EMPTY_RESPONSE = "Empty response"
    JUNK_RESPONSE = "Junk response"
    RESPONSE_TIMEOUT = "Response timeout"
    ZERO_RTT_REJECTED = "0-RTT rejected"
    HTTP_STATUS_401 = "HTTP status 401"
    HTTP_STATUS_403 = "HTTP status 403"
    HTTP_STATUS_404 = "HTTP status 404"
    HTTP_STATUS_408 = "HTTP status 408"
    HTTP_STATUS_425 = "HTTP status 425"
    HTTP_STATUS_500 = "HTTP status 500"
    HTTP_STATUS_501 = "HTTP status 501"
    HTTP_STATUS_502 = "HTTP status 502"
    HTTP_STATUS_503 = "HTTP status 503"
    HTTP_STATUS_504 = "HTTP status 504"


class HTTPRetryProperties(CoreApiModel):
    tries_amount: Optional[conint(ge=1, le=3)]
    tries_failover_amount: Optional[conint(ge=1, le=3)]
    conditions: List[HTTPRetryConditionEnum] = Field(..., unique_items=True)


class HealthStatusEnum(StrEnum):
    UP = "up"
    MAINTENANCE = "maintenance"


class HostEnum(StrEnum):
    ALL = "%"
    LOCALHOST_IPV6 = "::1"


class HostsEntryCreateRequest(CoreApiModel):
    node_id: int
    host_name: str
    cluster_id: int


class HtpasswdFileCreateRequest(CoreApiModel):
    unix_user_id: int


class HtpasswdUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=255)
    htpasswd_file_id: int
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)


class HtpasswdUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = None


class IPAddressFamilyEnum(StrEnum):
    IPV6 = "IPv6"
    IPV4 = "IPv4"


class IPAddressProductTypeEnum(StrEnum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"


class LanguageCodeEnum(StrEnum):
    NL = "nl"
    EN = "en"


class LoadBalancingMethodEnum(StrEnum):
    ROUND_ROBIN = "Round Robin"
    SOURCE_IP_ADDRESS = "Source IP Address"


class LogMethodEnum(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"
    HEAD = "HEAD"


class LogSortOrderEnum(StrEnum):
    ASC = "ASC"
    DESC = "DESC"


class MailAccountCreateRequest(CoreApiModel):
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    mail_domain_id: int
    password: constr(regex=r"^[ -~]+$", min_length=6, max_length=255)
    quota: Optional[int]


class MailAccountUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=6, max_length=255)] = None
    quota: Optional[int] = None


class MailAccountUsageIncludes(CoreApiModel):
    pass


class MailAccountUsageResource(CoreApiModel):
    mail_account_id: int
    usage: confloat(ge=0.0)
    timestamp: datetime
    includes: MailAccountUsageIncludes


class MailAliasCreateRequest(CoreApiModel):
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    mail_domain_id: int
    forward_email_addresses: List[EmailStr] = Field(..., min_items=1, unique_items=True)


class MailAliasUpdateRequest(CoreApiModel):
    forward_email_addresses: Optional[List[EmailStr]] = None


class MailDomainCreateRequest(CoreApiModel):
    domain: str
    unix_user_id: int
    catch_all_forward_email_addresses: List[EmailStr] = Field(..., unique_items=True)
    is_local: bool


class MailDomainUpdateRequest(CoreApiModel):
    catch_all_forward_email_addresses: Optional[List[EmailStr]] = None
    is_local: Optional[bool] = None


class MailHostnameCreateRequest(CoreApiModel):
    domain: str
    cluster_id: int
    certificate_id: int


class MailHostnameUpdateRequest(CoreApiModel):
    certificate_id: Optional[int] = None


class MariaDBEncryptionKeyCreateRequest(CoreApiModel):
    cluster_id: int


class MariaDBPrivilegeEnum(StrEnum):
    ALL = "ALL"
    SELECT = "SELECT"


class MeilisearchEnvironmentEnum(StrEnum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class NestedPathsDict(RootModelCollectionMixin, CoreApiModel):  # type: ignore[misc]
    __root__: Optional[Dict[str, Optional["NestedPathsDict"]]] = None


class NodeAddOnCreateRequest(CoreApiModel):
    node_id: int
    product: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64)
    quantity: int


class NodeAddOnProduct(CoreApiModel):
    uuid: UUID4
    name: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64)
    memory_gib: Optional[int]
    cpu_cores: Optional[int]
    disk_gib: Optional[int]
    price: confloat(ge=0.0)
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2)
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3)


class NodeGroupEnum(StrEnum):
    ADMIN = "Admin"
    APACHE = "Apache"
    PROFTPD = "ProFTPD"
    NGINX = "nginx"
    DOVECOT = "Dovecot"
    MARIADB = "MariaDB"
    POSTGRESQL = "PostgreSQL"
    PHP = "PHP"
    PASSENGER = "Passenger"
    BORG = "Borg"
    FAST_REDIRECT = "Fast Redirect"
    HAPROXY = "HAProxy"
    REDIS = "Redis"
    COMPOSER = "Composer"
    WP_CLI = "WP-CLI"
    KERNELCARE = "KernelCare"
    IMAGEMAGICK = "ImageMagick"
    WKHTMLTOPDF = "wkhtmltopdf"
    GNU_MAILUTILS = "GNU Mailutils"
    CLAMAV = "ClamAV"
    PUPPETEER = "Puppeteer"
    LIBREOFFICE = "LibreOffice"
    GHOSTSCRIPT = "Ghostscript"
    FFMPEG = "FFmpeg"
    DOCKER = "Docker"
    MEILISEARCH = "Meilisearch"
    NEW_RELIC = "New Relic"
    MALDET = "maldet"
    NODEJS = "NodeJS"
    GRAFANA = "Grafana"
    SINGLESTORE = "SingleStore"
    METABASE = "Metabase"
    ELASTICSEARCH = "Elasticsearch"
    RABBITMQ = "RabbitMQ"


class NodeMariaDBGroupProperties(CoreApiModel):
    is_master: bool


class NodeProduct(CoreApiModel):
    uuid: UUID4
    name: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)
    memory_gib: int
    cpu_cores: int
    disk_gib: int
    allow_upgrade_to: List[constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)]
    allow_downgrade_to: List[constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)]
    price: confloat(ge=0.0)
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2)
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3)


class NodeRabbitMQGroupProperties(CoreApiModel):
    is_master: bool


class NodeRedisGroupProperties(CoreApiModel):
    is_master: bool


class ObjectModelNameEnum(StrEnum):
    BORG_ARCHIVE = "BorgArchive"
    BORG_REPOSITORY = "BorgRepository"
    SERVICE_ACCOUNT_TO_CLUSTER = "ServiceAccountToCluster"
    SITE = "Site"
    SERVICE_ACCOUNT_TO_CUSTOMER = "ServiceAccountToCustomer"
    CLUSTER = "Cluster"
    CUSTOMER = "Customer"
    CMS = "CMS"
    FPM_POOL = "FPMPool"
    VIRTUAL_HOST = "VirtualHost"
    PASSENGER_APP = "PassengerApp"
    DATABASE = "Database"
    CERTIFICATE_MANAGER = "CertificateManager"
    BASIC_AUTHENTICATION_REALM = "BasicAuthenticationRealm"
    CRON = "Cron"
    DAEMON = "Daemon"
    MARIADB_ENCRYPTION_KEY = "MariaDBEncryptionKey"
    FIREWALL_RULE = "FirewallRule"
    HOSTS_ENTRY = "HostsEntry"
    NODE_ADD_ON = "NodeAddOn"
    IP_ADDRESS = "IPAddress"
    SECURITY_TXT_POLICY = "SecurityTXTPolicy"
    DATABASE_USER = "DatabaseUser"
    DATABASE_USER_GRANT = "DatabaseUserGrant"
    HTPASSWD_FILE = "HtpasswdFile"
    HTPASSWD_USER = "HtpasswdUser"
    MAIL_ACCOUNT = "MailAccount"
    MAIL_ALIAS = "MailAlias"
    MAIL_DOMAIN = "MailDomain"
    NODE = "Node"
    REDIS_INSTANCE = "RedisInstance"
    DOMAIN_ROUTER = "DomainRouter"
    MAIL_HOSTNAME = "MailHostname"
    CERTIFICATE = "Certificate"
    ROOT_SSH_KEY = "RootSSHKey"
    SSH_KEY = "SSHKey"
    UNIX_USER = "UNIXUser"
    UNIX_USER_RABBITMQ_CREDENTIALS = "UNIXUserRabbitMQCredentials"
    HAPROXY_LISTEN = "HAProxyListen"
    HAPROXY_LISTEN_TO_NODE = "HAProxyListenToNode"
    URL_REDIRECT = "URLRedirect"
    SITE_TO_CUSTOMER = "SiteToCustomer"
    SERVICE_ACCOUNT = "ServiceAccount"
    SERVICE_ACCOUNT_SERVER = "ServiceAccountServer"
    CUSTOM_CONFIG = "CustomConfig"
    CLUSTERS_PHP_PROPERTIES = "clusters_php_properties"
    CLUSTERS_NODEJS_PROPERTIES = "clusters_nodejs_properties"
    CLUSTERS_BORG_PROPERTIES = "clusters_borg_properties"
    CLUSTERS_KERNELCARE_PROPERTIES = "clusters_kernelcare_properties"
    CLUSTERS_NEW_RELIC_PROPERTIES = "clusters_new_relic_properties"
    CLUSTERS_REDIS_PROPERTIES = "clusters_redis_properties"
    CLUSTERS_POSTGRESQL_PROPERTIES = "clusters_postgresql_properties"
    CLUSTERS_MARIADB_PROPERTIES = "clusters_mariadb_properties"
    CLUSTERS_MEILISEARCH_PROPERTIES = "clusters_meilisearch_properties"
    CLUSTERS_GRAFANA_PROPERTIES = "clusters_grafana_properties"
    CLUSTERS_SINGLESTORE_PROPERTIES = "clusters_singlestore_properties"
    CLUSTERS_ELASTICSEARCH_PROPERTIES = "clusters_elasticsearch_properties"
    CLUSTERS_RABBITMQ_PROPERTIES = "clusters_rabbitmq_properties"
    CLUSTERS_METABASE_PROPERTIES = "clusters_metabase_properties"
    CLUSTERS_UNIX_USERS_PROPERTIES = "clusters_unix_users_properties"
    CLUSTERS_LOAD_BALANCING_PROPERTIES = "clusters_load_balancing_properties"
    CLUSTERS_FIREWALL_PROPERTIES = "clusters_firewall_properties"
    CLUSTERS_OS_PROPERTIES = "clusters_os_properties"


class PHPExtensionEnum(StrEnum):
    REDIS = "redis"
    IMAGICK = "imagick"
    SQLITE3 = "sqlite3"
    INTL = "intl"
    BCMATH = "bcmath"
    XDEBUG = "xdebug"
    PGSQL = "pgsql"
    SSH2 = "ssh2"
    LDAP = "ldap"
    MCRYPT = "mcrypt"
    XMLRPC = "xmlrpc"
    APCU = "apcu"
    TIDEWAYS = "tideways"
    SQLSRV = "sqlsrv"
    GMP = "gmp"
    VIPS = "vips"
    EXCIMER = "excimer"
    MAILPARSE = "mailparse"
    UV = "uv"
    AMQP = "amqp"
    MONGODB = "mongodb"


class PHPSettings(CoreApiModel):
    apc_enable_cli: bool = False
    opcache_file_cache: bool = False
    opcache_validate_timestamps: bool = True
    short_open_tag: bool = False
    error_reporting: constr(regex=r"^[A-Z&~_ ]+$", min_length=1, max_length=255) = (
        Field(
            "E_ALL & ~E_DEPRECATED & ~E_STRICT",
        )
    )
    opcache_memory_consumption: conint(ge=192, le=1024) = 192
    max_execution_time: conint(ge=30, le=120) = 120
    max_file_uploads: conint(ge=100, le=1000) = 100
    memory_limit: conint(ge=256, le=4096) = 256
    post_max_size: conint(ge=32, le=256) = 32
    upload_max_filesize: conint(ge=32, le=256) = 32
    tideways_api_key: Optional[
        constr(regex=r"^[a-zA-Z0-9_]+$", min_length=16, max_length=32)
    ] = None
    tideways_sample_rate: Optional[conint(ge=1, le=100)] = None
    newrelic_browser_monitoring_auto_instrument: bool = True


class PassengerAppTypeEnum(StrEnum):
    NODEJS = "NodeJS"


class PassengerEnvironmentEnum(StrEnum):
    PRODUCTION = "Production"
    DEVELOPMENT = "Development"


class RedisEvictionPolicyEnum(StrEnum):
    VOLATILE_TTL = "volatile-ttl"
    VOLATILE_RANDOM = "volatile-random"
    ALLKEYS_RANDOM = "allkeys-random"
    VOLATILE_LFU = "volatile-lfu"
    VOLATILE_LRU = "volatile-lru"
    ALLKEYS_LFU = "allkeys-lfu"
    ALLKEYS_LRU = "allkeys-lru"
    NOEVICTION = "noeviction"


class RedisInstanceCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    cluster_id: int
    password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    memory_limit: conint(ge=8)
    max_databases: int
    eviction_policy: RedisEvictionPolicyEnum


class RedisInstanceUpdateRequest(CoreApiModel):
    password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = None
    memory_limit: Optional[conint(ge=8)] = None
    max_databases: Optional[int] = None
    eviction_policy: Optional[RedisEvictionPolicyEnum] = None


class RootSSHKeyCreatePrivateRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    cluster_id: int
    private_key: str


class RootSSHKeyCreatePublicRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    cluster_id: int
    public_key: str


class SSHKeyCreatePrivateRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128)
    unix_user_id: int
    private_key: str


class SSHKeyCreatePublicRequest(CoreApiModel):
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128)
    unix_user_id: int
    public_key: str


class SecurityTXTPolicyCreateRequest(CoreApiModel):
    cluster_id: int
    expires_timestamp: datetime
    email_contacts: List[EmailStr] = Field(
        ...,
        unique_items=True,
    )
    url_contacts: List[AnyUrl] = Field(
        ...,
        unique_items=True,
    )
    encryption_key_urls: List[AnyUrl] = Field(..., unique_items=True)
    acknowledgment_urls: List[AnyUrl] = Field(..., unique_items=True)
    policy_urls: List[AnyUrl] = Field(..., unique_items=True)
    opening_urls: List[AnyUrl] = Field(..., unique_items=True)
    preferred_languages: List[LanguageCodeEnum] = Field(..., unique_items=True)


class SecurityTXTPolicyUpdateRequest(CoreApiModel):
    expires_timestamp: Optional[datetime] = None
    email_contacts: Optional[List[EmailStr]] = None
    url_contacts: Optional[List[AnyUrl]] = None
    encryption_key_urls: Optional[List[AnyUrl]] = None
    acknowledgment_urls: Optional[List[AnyUrl]] = None
    policy_urls: Optional[List[AnyUrl]] = None
    opening_urls: Optional[List[AnyUrl]] = None
    preferred_languages: Optional[List[LanguageCodeEnum]] = None


class ServiceAccountGroupEnum(StrEnum):
    SECURITY_TXT_POLICY_SERVER = "Security TXT Policy Server"
    LOAD_BALANCER = "Load Balancer"
    MAIL_PROXY = "Mail Proxy"
    MAIL_GATEWAY = "Mail Gateway"
    INTERNET_ROUTER = "Internet Router"
    STORAGE_ROUTER = "Storage Router"
    PHPMYADMIN = "phpMyAdmin"


class ShellPathEnum(StrEnum):
    BASH = "/bin/bash"
    JAILSHELL = "/usr/local/bin/jailshell"
    NOLOGIN = "/usr/sbin/nologin"


class SiteIncludes(CoreApiModel):
    pass


class SiteResource(CoreApiModel):
    id: int
    name: constr(regex=r"^[A-Z0-9-]+$", min_length=1, max_length=32)
    includes: SiteIncludes


class StatusCodeEnum(IntEnum):
    INTEGER_301 = 301
    INTEGER_302 = 302
    INTEGER_303 = 303
    INTEGER_307 = 307
    INTEGER_308 = 308


class TaskCollectionCallback(CoreApiModel):
    task_collection_uuid: UUID4
    success: bool


class TaskCollectionTypeEnum(StrEnum):
    ASYNCHRONOUS = "asynchronous"


class TaskStateEnum(StrEnum):
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class TemporaryFTPUserCreateRequest(CoreApiModel):
    unix_user_id: int
    node_id: int


class TemporaryFTPUserResource(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    file_manager_url: AnyUrl


class TimeUnitEnum(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TokenTypeEnum(StrEnum):
    BEARER = "bearer"


class UNIXUserComparison(CoreApiModel):
    not_identical_paths: NestedPathsDict
    only_left_files_paths: NestedPathsDict
    only_right_files_paths: NestedPathsDict
    only_left_directories_paths: NestedPathsDict
    only_right_directories_paths: NestedPathsDict


class UNIXUserCreateRequest(CoreApiModel):
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    virtual_hosts_directory: Optional[str]
    mail_domains_directory: Optional[str]
    borg_repositories_directory: Optional[str]
    cluster_id: int
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)]
    shell_path: ShellPathEnum
    record_usage_files: bool
    default_php_version: Optional[str]
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")]
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ]


class UNIXUserHomeDirectoryEnum(StrEnum):
    VAR_WWW_VHOSTS = "/var/www/vhosts"
    VAR_WWW = "/var/www"
    HOME = "/home"
    MNT_MAIL = "/mnt/mail"
    MNT_BACKUPS = "/mnt/backups"


class UNIXUserUpdateRequest(CoreApiModel):
    password: Optional[constr(regex=r"^[ -~]+$", min_length=24, max_length=255)] = None
    shell_path: Optional[ShellPathEnum] = None
    record_usage_files: Optional[bool] = None
    default_php_version: Optional[str] = None
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = None
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = None


class UNIXUserUsageFile(CoreApiModel):
    path: str
    size: confloat(ge=0.0)


class UNIXUserUsageIncludes(CoreApiModel):
    pass


class UNIXUserUsageResource(CoreApiModel):
    unix_user_id: int
    usage: confloat(ge=0.0)
    files: Optional[List[UNIXUserUsageFile]]
    timestamp: datetime
    includes: UNIXUserUsageIncludes


class UNIXUsersHomeDirectoryUsageIncludes(CoreApiModel):
    pass


class UNIXUsersHomeDirectoryUsageResource(CoreApiModel):
    cluster_id: int
    usage: confloat(ge=0.0)
    timestamp: datetime
    includes: UNIXUsersHomeDirectoryUsageIncludes


class URLRedirectCreateRequest(CoreApiModel):
    domain: str
    cluster_id: int
    server_aliases: List[str] = Field(
        ...,
        unique_items=True,
    )
    destination_url: AnyUrl
    status_code: StatusCodeEnum
    keep_query_parameters: bool
    keep_path: bool
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ]


class URLRedirectUpdateRequest(CoreApiModel):
    server_aliases: Optional[List[str]] = None
    destination_url: Optional[AnyUrl] = None
    status_code: Optional[StatusCodeEnum] = None
    keep_query_parameters: Optional[bool] = None
    keep_path: Optional[bool] = None
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = None


class ValidationError(CoreApiModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class VirtualHostDocumentRoot(CoreApiModel):
    contains_files: Dict[str, bool]


class VirtualHostServerSoftwareNameEnum(StrEnum):
    APACHE = "Apache"
    NGINX = "nginx"


class VirtualHostUpdateRequest(CoreApiModel):
    server_aliases: Optional[List[str]] = None
    document_root: Optional[str] = None
    fpm_pool_id: Optional[int] = None
    passenger_app_id: Optional[int] = None
    custom_config: Optional[
        constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    ] = None
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]] = None
    allow_override_option_directives: Optional[
        List[AllowOverrideOptionDirectiveEnum]
    ] = None
    server_software_name: Optional[VirtualHostServerSoftwareNameEnum] = None


class BorgArchiveContent(CoreApiModel):
    object_type: BorgArchiveContentObjectTypeEnum
    symbolic_mode: constr(regex=r"^[rwx\+\-dlsStT]+$", min_length=10, max_length=10)
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    group_name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    path: str
    link_target: Optional[str]
    modification_time: datetime
    size: Optional[conint(ge=0)]


class CMSCreateRequest(CoreApiModel):
    software_name: CMSSoftwareNameEnum
    is_manually_created: bool
    virtual_host_id: int


class CMSOption(CoreApiModel):
    value: conint(ge=0, le=1)
    name: CMSOptionNameEnum


class CertificateManagerCreateRequest(CoreApiModel):
    common_names: List[str] = Field(
        ...,
        min_items=1,
        unique_items=True,
    )
    provider_name: CertificateProviderNameEnum
    cluster_id: int
    request_callback_url: Optional[AnyUrl]


class ClusterCreateRequest(BaseModel):
    customer_id: int
    site_id: int
    description: constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255)


class ClusterDeploymentTaskResult(CoreApiModel):
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    message: Optional[str]
    state: TaskStateEnum


class ClusterIPAddressCreateRequest(CoreApiModel):
    service_account_name: str
    dns_name: str
    address_family: IPAddressFamilyEnum


class ClusterIncludes(CoreApiModel):
    site: SiteResource
    customer: CustomerResource


class ClusterResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    customer_id: int
    site_id: int
    description: constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255)
    includes: ClusterIncludes


class ClusterUpdateRequest(BaseModel):
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_. ]+$", min_length=1, max_length=255)
    ] = None


class ClustersCommonProperties(CoreApiModel):
    imap_hostname: str
    imap_port: int
    imap_encryption: EncryptionTypeEnum
    smtp_hostname: str
    smtp_port: int
    smtp_encryption: EncryptionTypeEnum
    pop3_hostname: str
    pop3_port: int
    pop3_encryption: EncryptionTypeEnum
    phpmyadmin_url: AnyUrl


class CustomConfigCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    server_software_name: CustomConfigServerSoftwareNameEnum
    cluster_id: int
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)


class CustomConfigIncludes(CoreApiModel):
    cluster: ClusterResource


class CustomConfigResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    cluster_id: int
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    server_software_name: CustomConfigServerSoftwareNameEnum
    includes: CustomConfigIncludes


class CustomConfigSnippetCreateFromContentsRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    server_software_name: VirtualHostServerSoftwareNameEnum
    cluster_id: int
    is_default: bool
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)


class CustomConfigSnippetCreateFromTemplateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    server_software_name: VirtualHostServerSoftwareNameEnum
    cluster_id: int
    is_default: bool
    template_name: CustomConfigSnippetTemplateNameEnum


class CustomConfigSnippetIncludes(CoreApiModel):
    cluster: ClusterResource


class CustomConfigSnippetResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    server_software_name: VirtualHostServerSoftwareNameEnum
    contents: constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)
    cluster_id: int
    is_default: bool
    includes: CustomConfigSnippetIncludes


class CustomerIPAddressCreateRequest(CoreApiModel):
    service_account_name: str
    dns_name: str
    address_family: IPAddressFamilyEnum


class DatabaseCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    server_software_name: DatabaseServerSoftwareNameEnum
    cluster_id: int
    optimizing_enabled: bool
    backups_enabled: bool


class DatabaseIncludes(CoreApiModel):
    cluster: ClusterResource


class DatabaseResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    server_software_name: DatabaseServerSoftwareNameEnum
    cluster_id: int
    optimizing_enabled: bool
    backups_enabled: bool
    includes: DatabaseIncludes


class DatabaseUserCreateRequest(CoreApiModel):
    password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    server_software_name: DatabaseServerSoftwareNameEnum
    host: Optional[HostEnum]
    cluster_id: int
    phpmyadmin_firewall_groups_ids: Optional[List[int]]


class DatabaseUserGrantCreateRequest(CoreApiModel):
    database_id: int
    database_user_id: int
    table_name: Optional[constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)]
    privilege_name: MariaDBPrivilegeEnum


class DatabaseUserIncludes(CoreApiModel):
    cluster: ClusterResource


class DatabaseUserResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    server_software_name: DatabaseServerSoftwareNameEnum
    host: Optional[HostEnum]
    cluster_id: int
    phpmyadmin_firewall_groups_ids: Optional[List[int]]
    includes: DatabaseUserIncludes


class FirewallGroupIncludes(CoreApiModel):
    cluster: ClusterResource


class FirewallGroupResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9_]+$", min_length=1, max_length=32)
    cluster_id: int
    ip_networks: List[str] = Field(
        ...,
        min_items=1,
        unique_items=True,
    )
    includes: FirewallGroupIncludes


class FirewallRuleCreateRequest(CoreApiModel):
    node_id: int
    firewall_group_id: Optional[int]
    external_provider_name: Optional[FirewallRuleExternalProviderNameEnum]
    service_name: Optional[FirewallRuleServiceNameEnum]
    haproxy_listen_id: Optional[int]
    port: Optional[int]


class HAProxyListenCreateRequest(CoreApiModel):
    name: constr(regex=r"^[a-z_]+$", min_length=1, max_length=64)
    cluster_id: int
    nodes_group: NodeGroupEnum
    nodes_ids: Optional[List[int]] = None
    port: Optional[conint(ge=3306, le=7700)]
    socket_path: Optional[str]
    load_balancing_method: LoadBalancingMethodEnum = Field(
        LoadBalancingMethodEnum.SOURCE_IP_ADDRESS,
    )
    destination_cluster_id: int


class HAProxyListenIncludes(CoreApiModel):
    destination_cluster: ClusterResource
    cluster: ClusterResource


class HAProxyListenResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z_]+$", min_length=1, max_length=64)
    cluster_id: int
    nodes_group: NodeGroupEnum
    nodes_ids: Optional[List[int]]
    port: Optional[conint(ge=3306, le=7700)]
    socket_path: Optional[str]
    load_balancing_method: Optional[LoadBalancingMethodEnum] = (
        LoadBalancingMethodEnum.SOURCE_IP_ADDRESS
    )
    destination_cluster_id: int
    includes: HAProxyListenIncludes


class HTTPValidationError(CoreApiModel):
    detail: Optional[List[ValidationError]] = None


class HealthResource(CoreApiModel):
    status: HealthStatusEnum


class IPAddressProduct(CoreApiModel):
    uuid: UUID4
    name: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64)
    type: IPAddressProductTypeEnum
    price: confloat(ge=0.0)
    period: constr(regex=r"^[A-Z0-9]+$", min_length=2, max_length=2)
    currency: constr(regex=r"^[A-Z]+$", min_length=3, max_length=3)


class WebServerLogAccessResource(CoreApiModel):
    remote_address: str
    raw_message: constr(min_length=1, max_length=65535)
    method: Optional[LogMethodEnum] = None
    uri: Optional[constr(min_length=1, max_length=65535)] = None
    timestamp: datetime
    status_code: int
    bytes_sent: conint(ge=0)


class WebServerLogErrorResource(CoreApiModel):
    remote_address: str
    raw_message: constr(min_length=1, max_length=65535)
    method: Optional[LogMethodEnum] = None
    uri: Optional[constr(min_length=1, max_length=65535)] = None
    timestamp: datetime
    error_message: constr(min_length=1, max_length=65535)


class MariaDBEncryptionKeyIncludes(CoreApiModel):
    cluster: ClusterResource


class MariaDBEncryptionKeyResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    identifier: int
    key: constr(regex=r"^[a-z0-9]+$", min_length=64, max_length=64)
    cluster_id: int
    includes: MariaDBEncryptionKeyIncludes


class NodeGroupDependency(CoreApiModel):
    is_dependency: bool
    impact: Optional[str]
    reason: str
    group: NodeGroupEnum


class NodeGroupsProperties(CoreApiModel):
    Redis: Optional[NodeRedisGroupProperties]
    MariaDB: Optional[NodeMariaDBGroupProperties]
    RabbitMQ: Optional[NodeRabbitMQGroupProperties]


class NodeIncludes(CoreApiModel):
    cluster: ClusterResource


class NodeResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    hostname: str
    product: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)
    cluster_id: int
    groups: List[NodeGroupEnum] = Field(
        ...,
        unique_items=True,
    )
    comment: Optional[constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)]
    load_balancer_health_checks_groups_pairs: Dict[NodeGroupEnum, List[NodeGroupEnum]]
    groups_properties: NodeGroupsProperties
    is_ready: bool
    includes: NodeIncludes


class NodeUpdateRequest(CoreApiModel):
    groups: Optional[List[NodeGroupEnum]] = None
    comment: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ] = None
    load_balancer_health_checks_groups_pairs: Optional[
        Dict[NodeGroupEnum, List[NodeGroupEnum]]
    ] = None


class PassengerAppCreateNodeJSRequest(CoreApiModel):
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    app_root: str
    unix_user_id: int
    environment: PassengerEnvironmentEnum
    environment_variables: Dict[
        constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")
    ]
    max_pool_size: int
    max_requests: int
    pool_idle_time: int
    is_namespaced: bool
    cpu_limit: Optional[int]
    nodejs_version: constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")
    startup_file: str


class PassengerAppUpdateRequest(CoreApiModel):
    environment: Optional[PassengerEnvironmentEnum] = None
    environment_variables: Optional[
        Dict[constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")]
    ] = None
    max_pool_size: Optional[int] = None
    max_requests: Optional[int] = None
    pool_idle_time: Optional[int] = None
    is_namespaced: Optional[bool] = None
    cpu_limit: Optional[int] = None
    nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")] = None
    startup_file: Optional[str] = None


class RedisInstanceIncludes(CoreApiModel):
    cluster: ClusterResource


class RedisInstanceResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    port: int
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    cluster_id: int
    password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    memory_limit: conint(ge=8)
    max_databases: int
    eviction_policy: RedisEvictionPolicyEnum
    includes: RedisInstanceIncludes


class RootSSHKeyIncludes(CoreApiModel):
    cluster: ClusterResource


class RootSSHKeyResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    public_key: Optional[str]
    private_key: Optional[str]
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    includes: RootSSHKeyIncludes


class SecurityTXTPolicyIncludes(CoreApiModel):
    cluster: ClusterResource


class SecurityTXTPolicyResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    expires_timestamp: datetime
    email_contacts: List[EmailStr] = Field(
        ...,
        unique_items=True,
    )
    url_contacts: List[AnyUrl] = Field(
        ...,
        unique_items=True,
    )
    encryption_key_urls: List[AnyUrl] = Field(..., unique_items=True)
    acknowledgment_urls: List[AnyUrl] = Field(..., unique_items=True)
    policy_urls: List[AnyUrl] = Field(..., unique_items=True)
    opening_urls: List[AnyUrl] = Field(..., unique_items=True)
    preferred_languages: List[LanguageCodeEnum] = Field(..., unique_items=True)
    includes: SecurityTXTPolicyIncludes


class TaskCollectionIncludes(CoreApiModel):
    cluster: Optional[ClusterResource]


class TaskCollectionResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    object_id: Optional[int]
    object_model_name: ObjectModelNameEnum
    uuid: UUID4
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    collection_type: TaskCollectionTypeEnum
    cluster_id: Optional[int]
    reference: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    includes: TaskCollectionIncludes


class TaskResult(CoreApiModel):
    description: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    uuid: UUID4
    message: Optional[str]
    state: TaskStateEnum
    retries: conint(ge=0)


class TokenResource(CoreApiModel):
    access_token: constr(regex=r"^[ -~]+$", min_length=1)
    token_type: TokenTypeEnum
    expires_in: int


class UNIXUserIncludes(CoreApiModel):
    cluster: ClusterResource


class UNIXUserResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    password: Optional[constr(regex=r"^[ -~]+$", min_length=1, max_length=255)]
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    unix_id: int
    home_directory: str
    ssh_directory: str
    virtual_hosts_directory: Optional[str]
    mail_domains_directory: Optional[str]
    borg_repositories_directory: Optional[str]
    cluster_id: int
    shell_path: ShellPathEnum
    record_usage_files: bool
    default_php_version: Optional[str]
    default_nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")]
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ]
    includes: UNIXUserIncludes


class URLRedirectIncludes(CoreApiModel):
    cluster: ClusterResource


class URLRedirectResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    domain: str
    cluster_id: int
    server_aliases: List[str] = Field(
        ...,
        unique_items=True,
    )
    destination_url: AnyUrl
    status_code: StatusCodeEnum
    keep_query_parameters: bool
    keep_path: bool
    description: Optional[
        constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)
    ]
    includes: URLRedirectIncludes


class VirtualHostCreateRequest(CoreApiModel):
    server_software_name: Optional[VirtualHostServerSoftwareNameEnum]
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]]
    allow_override_option_directives: Optional[List[AllowOverrideOptionDirectiveEnum]]
    domain: str
    public_root: str
    unix_user_id: int
    server_aliases: List[str] = Field(
        ...,
        unique_items=True,
    )
    document_root: str
    fpm_pool_id: Optional[int]
    passenger_app_id: Optional[int]
    custom_config: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)]


class BorgRepositoryIncludes(CoreApiModel):
    unix_user: Optional[UNIXUserResource]
    cluster: ClusterResource


class BorgRepositoryResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    passphrase: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    remote_host: str
    remote_path: str
    remote_username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=32)
    cluster_id: int
    keep_hourly: Optional[int]
    keep_daily: Optional[int]
    keep_weekly: Optional[int]
    keep_monthly: Optional[int]
    keep_yearly: Optional[int]
    identity_file_path: Optional[str]
    unix_user_id: Optional[int]
    includes: BorgRepositoryIncludes


class CertificateIncludes(CoreApiModel):
    cluster: ClusterResource


class CertificateResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    main_common_name: str
    common_names: List[str] = Field(..., min_items=1, unique_items=True)
    expires_at: datetime
    certificate: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    )
    ca_chain: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    )
    private_key: constr(
        regex=r"^[a-zA-Z0-9-_\+\/=\n\\ ]+$", min_length=1, max_length=65535
    )
    cluster_id: int
    includes: CertificateIncludes


class ClusterDeploymentResults(CoreApiModel):
    created_at: datetime
    tasks_results: List[ClusterDeploymentTaskResult]


class CronIncludes(CoreApiModel):
    cluster: ClusterResource
    unix_user: UNIXUserResource
    node: NodeResource


class CronResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    node_id: int
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    email_address: Optional[EmailStr]
    schedule: str
    error_count: int
    random_delay_max_seconds: int
    timeout_seconds: Optional[int]
    locking_enabled: bool
    is_active: bool
    memory_limit: Optional[conint(ge=256)]
    cpu_limit: Optional[int]
    includes: CronIncludes


class DaemonIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class DaemonResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int
    command: constr(regex=r"^[ -~]+$", min_length=1, max_length=65535)
    nodes_ids: List[int] = Field(..., min_items=1, unique_items=True)
    memory_limit: Optional[conint(ge=256)]
    cpu_limit: Optional[int]
    includes: DaemonIncludes


class DatabaseUserGrantIncludes(CoreApiModel):
    cluster: ClusterResource
    database: DatabaseResource
    database_user: DatabaseUserResource


class DatabaseUserGrantResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    database_id: int
    database_user_id: int
    table_name: Optional[constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)]
    privilege_name: MariaDBPrivilegeEnum
    includes: DatabaseUserGrantIncludes


class FPMPoolIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class FPMPoolResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    version: str
    unix_user_id: int
    max_children: int
    max_requests: int
    process_idle_timeout: int
    cpu_limit: Optional[int]
    log_slow_requests_threshold: Optional[int]
    is_namespaced: bool
    memory_limit: Optional[conint(ge=256)]
    includes: FPMPoolIncludes


class FTPUserIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class FTPUserResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)
    cluster_id: int
    username: constr(regex=r"^[a-z0-9-_.@]+$", min_length=1, max_length=32)
    unix_user_id: int
    directory_path: str
    includes: FTPUserIncludes


class FirewallRuleIncludes(CoreApiModel):
    node: NodeResource
    firewall_group: Optional[FirewallGroupResource]
    haproxy_listen: Optional[HAProxyListenResource]
    cluster: ClusterResource


class FirewallRuleResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    node_id: int
    firewall_group_id: Optional[int]
    external_provider_name: Optional[FirewallRuleExternalProviderNameEnum]
    service_name: Optional[FirewallRuleServiceNameEnum]
    haproxy_listen_id: Optional[int]
    port: Optional[int]
    includes: FirewallRuleIncludes


class HAProxyListenToNodeIncludes(CoreApiModel):
    haproxy_listen: HAProxyListenResource
    node: NodeResource
    cluster: ClusterResource


class HAProxyListenToNodeResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    haproxy_listen_id: int
    node_id: int
    includes: HAProxyListenToNodeIncludes


class HostsEntryIncludes(CoreApiModel):
    node: NodeResource
    cluster: ClusterResource


class HostsEntryResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    node_id: int
    host_name: str
    cluster_id: int
    includes: HostsEntryIncludes


class HtpasswdFileIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class HtpasswdFileResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    unix_user_id: int
    includes: HtpasswdFileIncludes


class HtpasswdUserIncludes(CoreApiModel):
    htpasswd_file: HtpasswdFileResource
    cluster: ClusterResource


class HtpasswdUserResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)
    cluster_id: int
    username: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=255)
    htpasswd_file_id: int
    includes: HtpasswdUserIncludes


class MailDomainIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class MailDomainResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    domain: str
    unix_user_id: int
    catch_all_forward_email_addresses: List[EmailStr] = Field(..., unique_items=True)
    is_local: bool
    includes: MailDomainIncludes


class MailHostnameIncludes(CoreApiModel):
    certificate: CertificateResource
    cluster: ClusterResource


class MailHostnameResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    domain: str
    cluster_id: int
    certificate_id: int
    includes: MailHostnameIncludes


class MalwareIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class MalwareResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    unix_user_id: int
    name: constr(regex=r"^\{([A-Z]+)\}[a-zA-Z0-9-_.]+$", min_length=1, max_length=255)
    path: str
    last_seen_at: datetime
    includes: MalwareIncludes


class NodeAddOnIncludes(CoreApiModel):
    node: NodeResource
    cluster: ClusterResource


class NodeAddOnResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    node_id: int
    product: constr(regex=r"^[a-zA-Z0-9 ]+$", min_length=1, max_length=64)
    quantity: int
    includes: NodeAddOnIncludes


class NodeCreateRequest(CoreApiModel):
    product: constr(regex=r"^[A-Z]+$", min_length=1, max_length=2)
    cluster_id: int
    groups: List[NodeGroupEnum] = Field(
        ...,
        unique_items=True,
    )
    comment: Optional[constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=255)]
    load_balancer_health_checks_groups_pairs: Dict[NodeGroupEnum, List[NodeGroupEnum]]


class NodeCronDependency(CoreApiModel):
    is_dependency: bool
    impact: Optional[str]
    reason: str
    cron: CronResource


class NodeDaemonDependency(CoreApiModel):
    is_dependency: bool
    impact: Optional[str]
    reason: str
    daemon: DaemonResource


class NodeHostsEntryDependency(CoreApiModel):
    is_dependency: bool
    impact: Optional[str]
    reason: str
    hosts_entry: HostsEntryResource


class PassengerAppIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class PassengerAppResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    port: int
    app_type: PassengerAppTypeEnum
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    app_root: str
    unix_user_id: int
    environment: PassengerEnvironmentEnum
    environment_variables: Dict[
        constr(regex=r"^[A-Za-z_]+$"), constr(regex=r"^[ -~]+$")
    ]
    max_pool_size: int
    max_requests: int
    pool_idle_time: int
    is_namespaced: bool
    cpu_limit: Optional[int]
    includes: PassengerAppIncludes
    nodejs_version: Optional[constr(regex=r"^[0-9]{1,2}\.[0-9]{1,2}$")]
    startup_file: Optional[str]


class SSHKeyIncludes(CoreApiModel):
    unix_user: UNIXUserResource
    cluster: ClusterResource


class SSHKeyResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    public_key: Optional[str]
    private_key: Optional[str]
    identity_file_path: Optional[str]
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=128)
    unix_user_id: int
    includes: SSHKeyIncludes


class VirtualHostIncludes(CoreApiModel):
    cluster: ClusterResource
    unix_user: UNIXUserResource
    fpm_pool: Optional[FPMPoolResource]
    passenger_app: Optional[PassengerAppResource]


class VirtualHostResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    unix_user_id: int
    server_software_name: VirtualHostServerSoftwareNameEnum
    allow_override_directives: Optional[List[AllowOverrideDirectiveEnum]]
    allow_override_option_directives: Optional[List[AllowOverrideOptionDirectiveEnum]]
    domain_root: str
    cluster_id: int
    domain: str
    public_root: str
    server_aliases: List[str] = Field(
        ...,
        unique_items=True,
    )
    document_root: str
    fpm_pool_id: Optional[int]
    passenger_app_id: Optional[int]
    custom_config: Optional[constr(regex=r"^[ -~\n]+$", min_length=1, max_length=65535)]
    includes: VirtualHostIncludes


class BasicAuthenticationRealmIncludes(CoreApiModel):
    htpasswd_file: HtpasswdFileResource
    virtual_host: VirtualHostResource
    cluster: ClusterResource


class BasicAuthenticationRealmResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    directory_path: Optional[str]
    virtual_host_id: int
    name: constr(regex=r"^[a-zA-Z0-9-_ ]+$", min_length=1, max_length=64)
    htpasswd_file_id: int
    includes: BasicAuthenticationRealmIncludes


class BorgArchiveIncludes(CoreApiModel):
    borg_repository: BorgRepositoryResource
    cluster: ClusterResource
    unix_user: Optional[UNIXUserResource]
    database: Optional[DatabaseResource]


class BorgArchiveResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    database_id: Optional[int]
    unix_user_id: Optional[int]
    cluster_id: int
    borg_repository_id: int
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    includes: BorgArchiveIncludes


class CMSIncludes(CoreApiModel):
    virtual_host: VirtualHostResource
    cluster: ClusterResource


class CMSResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    software_name: CMSSoftwareNameEnum
    is_manually_created: bool
    virtual_host_id: int
    includes: CMSIncludes


class CertificateManagerIncludes(CoreApiModel):
    certificate: Optional[CertificateResource]
    cluster: ClusterResource


class CertificateManagerResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    main_common_name: str
    certificate_id: Optional[int]
    last_request_task_collection_uuid: Optional[UUID4]
    common_names: List[str] = Field(
        ...,
        min_items=1,
        unique_items=True,
    )
    provider_name: CertificateProviderNameEnum
    cluster_id: int
    request_callback_url: Optional[AnyUrl]
    includes: CertificateManagerIncludes


class DomainRouterIncludes(CoreApiModel):
    virtual_host: Optional[VirtualHostResource]
    url_redirect: Optional[URLRedirectResource]
    node: Optional[NodeResource]
    certificate: Optional[CertificateResource]
    security_txt_policy: Optional[SecurityTXTPolicyResource]
    cluster: ClusterResource


class DomainRouterResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    domain: str
    virtual_host_id: Optional[int]
    url_redirect_id: Optional[int]
    category: DomainRouterCategoryEnum
    cluster_id: int
    node_id: Optional[int]
    certificate_id: Optional[int]
    security_txt_policy_id: Optional[int]
    firewall_groups_ids: Optional[List[int]]
    force_ssl: bool
    includes: DomainRouterIncludes


class MailAccountIncludes(CoreApiModel):
    mail_domain: MailDomainResource
    cluster: ClusterResource


class MailAccountResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    password: constr(regex=r"^[ -~]+$", min_length=1, max_length=255)
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    mail_domain_id: int
    cluster_id: int
    quota: Optional[int]
    includes: MailAccountIncludes


class MailAliasIncludes(CoreApiModel):
    mail_domain: MailDomainResource
    cluster: ClusterResource


class MailAliasResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    cluster_id: int
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    mail_domain_id: int
    forward_email_addresses: List[EmailStr] = Field(..., min_items=1, unique_items=True)
    includes: MailAliasIncludes


class NodeDomainRouterDependency(CoreApiModel):
    is_dependency: bool
    impact: Optional[str]
    reason: str
    domain_router: DomainRouterResource


class TombstoneDataCertificateIncludes(BaseModel):
    pass


class TombstoneDataDaemonIncludes(BaseModel):
    pass


class TombstoneDataDatabaseIncludes(BaseModel):
    pass


class TombstoneDataFPMPoolIncludes(BaseModel):
    pass


class TombstoneDataPassengerAppIncludes(BaseModel):
    pass


class TombstoneDataRedisInstanceIncludes(BaseModel):
    pass


class TombstoneDataUNIXUserIncludes(BaseModel):
    pass


class TombstoneDataUNIXUserRabbitMQCredentialsIncludes(BaseModel):
    pass


class TombstoneDataVirtualHostIncludes(BaseModel):
    pass


class TombstoneDataDatabaseUserIncludes(BaseModel):
    pass


class TombstoneDataDomainRouterIncludes(BaseModel):
    pass


class TombstoneDataRootSSHKeyIncludes(BaseModel):
    pass


class TombstoneDataSSHKeyIncludes(BaseModel):
    pass


class TombstoneDataMailHostnameIncludes(BaseModel):
    pass


class TombstoneDataCustomConfigIncludes(BaseModel):
    pass


class TombstoneDataDatabaseUser(BaseModel):
    id: int
    data_type: Literal["database_user"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    host: Optional[HostEnum]
    server_software_name: DatabaseServerSoftwareNameEnum
    includes: TombstoneDataDatabaseUserIncludes


class TombstoneDataDatabase(CoreApiModel):
    id: int
    data_type: Literal["database"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=63)
    server_software_name: DatabaseServerSoftwareNameEnum
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataDatabaseIncludes


class TombstoneDataDatabaseUserGrantIncludes(BaseModel):
    id: int
    database: Union[DatabaseResource, TombstoneDataDatabase]
    database_user: Union[DatabaseUserResource, TombstoneDataDatabaseUser]


class TombstoneDataDatabaseUserGrant(BaseModel):
    id: int
    data_type: Literal["database_user_grant"]
    table_name: Optional[constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)]
    privilege_name: MariaDBPrivilegeEnum
    database_id: int
    database_user_id: int
    includes: TombstoneDataDatabaseUserGrantIncludes


class TombstoneDataDomainRouter(BaseModel):
    id: int
    data_type: Literal["domain_router"]
    domain: str
    includes: TombstoneDataDomainRouterIncludes


class TombstoneDataRootSSHKey(BaseModel):
    id: int
    data_type: Literal["root_ssh_key"]
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    is_private_key: bool
    includes: TombstoneDataRootSSHKeyIncludes


class TombstoneDataSSHKey(BaseModel):
    id: int
    data_type: Literal["ssh_key"]
    name: constr(regex=r"^[a-zA-Z0-9-_]+$", min_length=1, max_length=64)
    identity_file_path: Optional[str]
    includes: TombstoneDataSSHKeyIncludes


class TombstoneDataMailHostname(BaseModel):
    id: int
    data_type: Literal["mail_hostname"]
    domain: str
    includes: TombstoneDataMailHostnameIncludes


class TombstoneDataCertificate(CoreApiModel):
    id: int
    data_type: Literal["certificate"]
    includes: TombstoneDataCertificateIncludes


class TombstoneDataDaemon(CoreApiModel):
    id: int
    data_type: Literal["daemon"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    nodes_ids: List[int] = Field(..., min_items=1, unique_items=True)
    includes: TombstoneDataDaemonIncludes


class TombstoneDataFPMPool(CoreApiModel):
    id: int
    data_type: Literal["fpm_pool"]
    version: str
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    includes: TombstoneDataFPMPoolIncludes


class TombstoneDataPassengerApp(CoreApiModel):
    id: int
    data_type: Literal["passenger_app"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    app_root: str
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataPassengerAppIncludes


class TombstoneDataRedisInstance(CoreApiModel):
    id: int
    data_type: Literal["redis_instance"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataRedisInstanceIncludes


class TombstoneDataUNIXUser(CoreApiModel):
    id: int
    data_type: Literal["unix_user"]
    home_directory: str
    mail_domains_directory: Optional[str]
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataUNIXUserIncludes


class TombstoneDataCronIncludes(BaseModel):
    node: NodeResource
    unix_user: Union[TombstoneDataUNIXUser, UNIXUserResource]


class TombstoneDataHtpasswdFileIncludes(BaseModel):
    unix_user: Union[UNIXUserResource, TombstoneDataUNIXUser]


class TombstoneDataHtpasswdFile(BaseModel):
    id: int
    data_type: Literal["htpasswd_file"]
    unix_user_id: int
    includes: TombstoneDataHtpasswdFileIncludes


class TombstoneDataMailDomainIncludes(BaseModel):
    unix_user: Union[UNIXUserResource, TombstoneDataUNIXUser]


class TombstoneDataMailDomain(BaseModel):
    id: int
    data_type: Literal["mail_domain"]
    domain: str
    unix_user_id: int
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataMailDomainIncludes


class TombstoneDataMailAccountIncludes(BaseModel):
    mail_domain: Union[MailDomainResource, TombstoneDataMailDomain]


class TombstoneDataMailAccount(CoreApiModel):
    id: int
    data_type: Literal["mail_account"]
    local_part: constr(regex=r"^[a-z0-9-.]+$", min_length=1, max_length=64)
    mail_domain_id: int
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataMailAccountIncludes


class TombstoneDataCron(CoreApiModel):
    id: int
    data_type: Literal["cron"]
    node_id: int
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=64)
    unix_user_id: int
    includes: TombstoneDataCronIncludes


class TombstoneDataUNIXUserRabbitMQCredentials(CoreApiModel):
    id: int
    data_type: Literal["unix_user_rabbitmq_credentials"]
    rabbitmq_virtual_host_name: constr(
        regex=r"^[a-z0-9-.]+$", min_length=1, max_length=32
    )
    includes: TombstoneDataUNIXUserRabbitMQCredentialsIncludes


class TombstoneDataVirtualHost(CoreApiModel):
    id: int
    data_type: Literal["virtual_host"]
    domain_root: str
    delete_on_cluster: Optional[bool] = False
    includes: TombstoneDataVirtualHostIncludes


class TombstoneDataCustomConfig(CoreApiModel):
    id: int
    data_type: Literal["custom_config"]
    name: constr(regex=r"^[a-z0-9-_]+$", min_length=1, max_length=128)
    includes: TombstoneDataCustomConfigIncludes


class TombstoneIncludes(CoreApiModel):
    cluster: ClusterResource


class TombstoneResource(CoreApiModel):
    id: int
    created_at: datetime
    updated_at: datetime
    data: Union[
        TombstoneDataPassengerApp,
        TombstoneDataCertificate,
        TombstoneDataFPMPool,
        TombstoneDataUNIXUserRabbitMQCredentials,
        TombstoneDataUNIXUser,
        TombstoneDataCron,
        TombstoneDataDaemon,
        TombstoneDataDatabase,
        TombstoneDataMailAccount,
        TombstoneDataRedisInstance,
        TombstoneDataVirtualHost,
        TombstoneDataDatabaseUser,
        TombstoneDataDatabaseUserGrant,
        TombstoneDataDomainRouter,
        TombstoneDataHtpasswdFile,
        TombstoneDataRootSSHKey,
        TombstoneDataSSHKey,
        TombstoneDataMailDomain,
        TombstoneDataMailHostname,
        TombstoneDataCustomConfig,
    ] = Field(
        ...,
        discriminator="data_type",
    )
    object_id: int
    object_model_name: ObjectModelNameEnum
    cluster_id: int
    includes: TombstoneIncludes


class NodeDependenciesResource(CoreApiModel):
    hostname: str
    groups: List[NodeGroupDependency]
    domain_routers: List[NodeDomainRouterDependency]
    daemons: List[NodeDaemonDependency]
    crons: List[NodeCronDependency]
    hosts_entries: List[NodeHostsEntryDependency]


class DaemonLogResource(BaseModel):
    application_name: constr(min_length=1, max_length=65535)
    priority: int
    pid: int
    message: constr(min_length=1, max_length=65535)
    node_hostname: str
    timestamp: datetime


class NodeSpecificationsResource(BaseModel):
    hostname: str
    memory_mib: int
    cpu_cores: int
    disk_gib: int
    usable_cpu_cores: int
    usable_memory_mib: int
    usable_disk_gib: int


class RequestLogIncludes(BaseModel):
    pass


class RequestLogResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    ip_address: str
    path: str
    method: HTTPMethod
    query_parameters: Dict[str, str]
    body: Any
    api_user_id: int
    request_id: UUID4
    includes: RequestLogIncludes


class ObjectLogIncludes(BaseModel):
    customer: Optional[CustomerResource]


class ObjectLogResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    object_id: int
    object_model_name: Optional[
        constr(regex=r"^[a-zA-Z]+$", min_length=1, max_length=255)
    ]
    request_id: Optional[UUID4]
    type: ObjectLogTypeEnum
    causer_type: Optional[CauserTypeEnum]
    causer_id: Optional[int]
    customer_id: Optional[int]
    includes: ObjectLogIncludes


class SimpleSpecificationsResource(RootModelCollectionMixin, BaseModel):  # type: ignore[misc]
    __root__: List[str]


class ConcreteSpecificationSatisfyResult(BaseModel):
    satisfied: bool
    requirement: str


class ConcreteSpecificationSatisfyResultResource(BaseModel):
    satisfied: bool
    requirement: str


class CompositeSpecificationSatisfyResult(BaseModel):
    name: str
    results: List[
        Union[ConcreteSpecificationSatisfyResult, "CompositeSpecificationSatisfyResult"]
    ]
    mode: SpecificationMode


class CompositeSpecificationSatisfyResultResource(BaseModel):
    name: str
    satisfied: bool
    results: List[
        Union[
            ConcreteSpecificationSatisfyResultResource,
            "CompositeSpecificationSatisfyResultResource",
        ]
    ]
    mode: SpecificationMode


class ClusterBorgPropertiesCreateRequest(BaseModel):
    automatic_borg_repositories_prune_enabled: bool = True


class ClusterBorgPropertiesIncludes(BaseModel):
    pass


class ClusterBorgPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    automatic_borg_repositories_prune_enabled: bool
    cluster_id: int
    includes: ClusterBorgPropertiesIncludes


class ClusterBorgPropertiesUpdateRequest(BaseModel):
    automatic_borg_repositories_prune_enabled: Optional[bool] = None


class ClusterElasticsearchPropertiesCreateRequest(BaseModel):
    elasticsearch_default_users_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )
    kibana_domain: str


class ClusterElasticsearchPropertiesIncludes(BaseModel):
    pass


class ClusterElasticsearchPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    elasticsearch_default_users_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )
    kibana_domain: str
    cluster_id: int
    includes: ClusterElasticsearchPropertiesIncludes


class ClusterElasticsearchPropertiesUpdateRequest(BaseModel):
    elasticsearch_default_users_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = None
    kibana_domain: Optional[str] = None


class ClusterFirewallPropertiesCreateRequest(BaseModel):
    firewall_rules_external_providers_enabled: bool = False


class ClusterFirewallPropertiesIncludes(BaseModel):
    pass


class ClusterFirewallPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    firewall_rules_external_providers_enabled: bool
    cluster_id: int
    includes: ClusterFirewallPropertiesIncludes


class ClusterFirewallPropertiesUpdateRequest(BaseModel):
    firewall_rules_external_providers_enabled: Optional[bool] = None


class ClusterGrafanaPropertiesCreateRequest(BaseModel):
    grafana_domain: str


class ClusterGrafanaPropertiesIncludes(BaseModel):
    pass


class ClusterGrafanaPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    grafana_domain: str
    cluster_id: int
    includes: ClusterGrafanaPropertiesIncludes


class ClusterGrafanaPropertiesUpdateRequest(BaseModel):
    grafana_domain: Optional[str] = None


class ClusterKernelcarePropertiesCreateRequest(BaseModel):
    kernelcare_license_key: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16
    )


class ClusterKernelcarePropertiesIncludes(BaseModel):
    pass


class ClusterKernelcarePropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    kernelcare_license_key: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16
    )
    cluster_id: int
    includes: ClusterKernelcarePropertiesIncludes


class ClusterKernelcarePropertiesUpdateRequest(BaseModel):
    kernelcare_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=16)
    ] = None


class ClusterLoadBalancingPropertiesIncludes(BaseModel):
    pass


class ClusterMariadbPropertiesCreateRequest(BaseModel):
    mariadb_version: str
    mariadb_backup_interval: conint(ge=1, le=24) = 24
    mariadb_backup_local_retention: conint(ge=1, le=24) = 3


class ClusterMariadbPropertiesIncludes(BaseModel):
    pass


class ClusterMariadbPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    mariadb_version: str
    mariadb_cluster_name: constr(regex=r"^[a-z.]+$", min_length=1, max_length=64)
    mariadb_backup_interval: conint(ge=1, le=24)
    mariadb_backup_local_retention: conint(ge=1, le=24)
    cluster_id: int
    includes: ClusterMariadbPropertiesIncludes


class ClusterMariadbPropertiesUpdateRequest(BaseModel):
    mariadb_backup_interval: Optional[conint(ge=1, le=24)] = None
    mariadb_backup_local_retention: Optional[conint(ge=1, le=24)] = None


class ClusterMeilisearchPropertiesIncludes(BaseModel):
    pass


class ClusterMetabasePropertiesCreateRequest(BaseModel):
    metabase_domain: str


class ClusterMetabasePropertiesIncludes(BaseModel):
    pass


class ClusterMetabasePropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    metabase_domain: str
    metabase_database_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    cluster_id: int
    includes: ClusterMetabasePropertiesIncludes


class ClusterMetabasePropertiesUpdateRequest(BaseModel):
    metabase_domain: Optional[str] = None
    metabase_database_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = None


class ClusterNewRelicPropertiesCreateRequest(BaseModel):
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = None
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = None


class ClusterNewRelicPropertiesIncludes(BaseModel):
    pass


class ClusterNewRelicPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    new_relic_mariadb_password: constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ]
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ]
    cluster_id: int
    includes: ClusterNewRelicPropertiesIncludes


class ClusterNewRelicPropertiesUpdateRequest(BaseModel):
    new_relic_mariadb_password: Optional[
        constr(regex=r"^[ -~]+$", min_length=24, max_length=255)
    ] = None
    new_relic_apm_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = None
    new_relic_infrastructure_license_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=40, max_length=40)
    ] = None


class ClusterNodejsPropertiesCreateRequest(BaseModel):
    nodejs_versions: List[str] = Field(
        ...,
        unique_items=True,
    )
    nodejs_version: Optional[int] = None


class ClusterNodejsPropertiesIncludes(BaseModel):
    pass


class ClusterNodejsPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    nodejs_version: Optional[int]
    nodejs_versions: List[NodejsVersion] = Field(
        ...,
        unique_items=True,
    )
    cluster_id: int
    includes: ClusterNodejsPropertiesIncludes


class ClusterNodejsPropertiesUpdateRequest(BaseModel):
    nodejs_versions: Optional[List[str]] = None


class ClusterOsPropertiesCreateRequest(BaseModel):
    automatic_upgrades_enabled: bool = False


class ClusterOsPropertiesIncludes(BaseModel):
    pass


class ClusterOsPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    automatic_upgrades_enabled: bool
    cluster_id: int
    includes: ClusterOsPropertiesIncludes


class ClusterOsPropertiesUpdateRequest(BaseModel):
    automatic_upgrades_enabled: Optional[bool] = None


class ClusterPhpPropertiesIncludes(BaseModel):
    pass


class ClusterPostgresqlPropertiesCreateRequest(BaseModel):
    postgresql_version: int
    postgresql_backup_local_retention: conint(ge=1, le=24) = 3
    postgresql_backup_interval: conint(ge=1, le=24) = 24


class ClusterPostgresqlPropertiesIncludes(BaseModel):
    pass


class ClusterPostgresqlPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    postgresql_version: int
    postgresql_backup_local_retention: conint(ge=1, le=24)
    postgresql_backup_interval: conint(ge=1, le=24)
    cluster_id: int
    includes: ClusterPostgresqlPropertiesIncludes


class ClusterPostgresqlPropertiesUpdateRequest(BaseModel):
    postgresql_backup_local_retention: Optional[conint(ge=1, le=24)] = None
    postgresql_backup_interval: Optional[conint(ge=1, le=24)] = None


class ClusterRabbitmqPropertiesCreateRequest(BaseModel):
    rabbitmq_admin_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )
    rabbitmq_management_domain: str


class ClusterRabbitmqPropertiesIncludes(BaseModel):
    pass


class ClusterRabbitmqPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    rabbitmq_erlang_cookie: constr(regex=r"^[A-Z0-9]+$", min_length=20, max_length=20)
    rabbitmq_admin_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )
    rabbitmq_management_domain: str
    cluster_id: int
    includes: ClusterRabbitmqPropertiesIncludes


class ClusterRabbitmqPropertiesUpdateRequest(BaseModel):
    rabbitmq_admin_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = None
    rabbitmq_management_domain: Optional[str] = None


class ClusterRedisPropertiesCreateRequest(BaseModel):
    redis_password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    redis_memory_limit: int


class ClusterRedisPropertiesIncludes(BaseModel):
    pass


class ClusterRedisPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    redis_password: constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    redis_memory_limit: int
    cluster_id: int
    includes: ClusterRedisPropertiesIncludes


class ClusterRedisPropertiesUpdateRequest(BaseModel):
    redis_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = None
    redis_memory_limit: Optional[int] = None


class ClusterSinglestorePropertiesCreateRequest(BaseModel):
    singlestore_studio_domain: str
    singlestore_api_domain: str
    singlestore_license_key: constr(regex=r"^[ -~]+$", min_length=144, max_length=144)
    singlestore_root_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )


class ClusterSinglestorePropertiesIncludes(BaseModel):
    pass


class ClusterSinglestorePropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    singlestore_studio_domain: str
    singlestore_api_domain: str
    singlestore_license_key: constr(regex=r"^[ -~]+$", min_length=144, max_length=6144)
    singlestore_root_password: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255
    )
    cluster_id: int
    includes: ClusterSinglestorePropertiesIncludes


class ClusterSinglestorePropertiesUpdateRequest(BaseModel):
    singlestore_studio_domain: Optional[str] = None
    singlestore_api_domain: Optional[str] = None
    singlestore_license_key: Optional[
        constr(regex=r"^[ -~]+$", min_length=144, max_length=144)
    ] = None
    singlestore_root_password: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=24, max_length=255)
    ] = None


class ClusterUnixUsersPropertiesIncludes(BaseModel):
    pass


class ClusterLoadBalancingPropertiesCreateRequest(BaseModel):
    http_retry_properties: HTTPRetryProperties = Field(
        default_factory=lambda: HTTPRetryProperties.parse_obj({"conditions": []})
    )
    load_balancing_method: LoadBalancingMethodEnum = LoadBalancingMethodEnum.ROUND_ROBIN


class ClusterLoadBalancingPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    http_retry_properties: HTTPRetryProperties
    load_balancing_method: LoadBalancingMethodEnum
    cluster_id: int
    includes: ClusterLoadBalancingPropertiesIncludes


class ClusterLoadBalancingPropertiesUpdateRequest(BaseModel):
    http_retry_properties: Optional[HTTPRetryProperties] = None
    load_balancing_method: Optional[LoadBalancingMethodEnum] = None


class ClusterMeilisearchPropertiesCreateRequest(BaseModel):
    meilisearch_backup_local_retention: conint(ge=1, le=24) = 3
    meilisearch_master_key: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24
    )
    meilisearch_environment: MeilisearchEnvironmentEnum
    meilisearch_backup_interval: conint(ge=1, le=24) = 24


class ClusterMeilisearchPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    meilisearch_backup_local_retention: conint(ge=1, le=24)
    meilisearch_master_key: constr(
        regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24
    )
    meilisearch_environment: MeilisearchEnvironmentEnum
    meilisearch_backup_interval: conint(ge=1, le=24)
    cluster_id: int
    includes: ClusterMeilisearchPropertiesIncludes


class ClusterMeilisearchPropertiesUpdateRequest(BaseModel):
    meilisearch_backup_local_retention: Optional[conint(ge=1, le=24)] = None
    meilisearch_master_key: Optional[
        constr(regex=r"^[a-zA-Z0-9]+$", min_length=16, max_length=24)
    ] = None
    meilisearch_environment: Optional[MeilisearchEnvironmentEnum] = None
    meilisearch_backup_interval: Optional[conint(ge=1, le=24)] = None


class ClusterPhpPropertiesCreateRequest(BaseModel):
    php_versions: List[str] = Field(
        ...,
        unique_items=True,
    )
    custom_php_modules_names: List[PHPExtensionEnum] = Field(
        ...,
        unique_items=True,
    )
    php_settings: PHPSettings
    php_ioncube_enabled: bool = False
    php_sessions_spread_enabled: bool = True


class ClusterPhpPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    php_versions: List[str] = Field(
        ...,
        unique_items=True,
    )
    custom_php_modules_names: List[PHPExtensionEnum] = Field(
        ...,
        unique_items=True,
    )
    php_settings: PHPSettings
    php_ioncube_enabled: bool
    php_sessions_spread_enabled: bool
    cluster_id: int
    includes: ClusterPhpPropertiesIncludes


class ClusterPhpPropertiesUpdateRequest(BaseModel):
    php_versions: Optional[List[str]] = None
    custom_php_modules_names: Optional[List[PHPExtensionEnum]] = None
    php_settings: Optional[PHPSettings] = None
    php_ioncube_enabled: Optional[bool] = None
    php_sessions_spread_enabled: Optional[bool] = None


class ClusterUnixUsersPropertiesCreateRequest(BaseModel):
    unix_users_home_directory: UNIXUserHomeDirectoryEnum = (
        UNIXUserHomeDirectoryEnum.HOME
    )


class ClusterUnixUsersPropertiesResource(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    unix_users_home_directory: UNIXUserHomeDirectoryEnum
    cluster_id: int
    includes: ClusterUnixUsersPropertiesIncludes


class SpecificationNameEnum(StrEnum):
    CLUSTER_SUPPORTS_VIRTUAL_HOSTS = "Cluster supports virtual hosts"
    CLUSTER_SUPPORTS_MARIADB_ENCRYPTION_KEYS = (
        "Cluster supports MariaDB encryption keys"
    )
    CLUSTER_SUPPORTS_MARIADB_DATABASES = "Cluster supports MariaDB databases"
    CLUSTER_SUPPORTS_MARIADB_DATABASE_USERS = "Cluster supports MariaDB database users"
    CLUSTER_SUPPORTS_POSTGRESQL_DATABASES = "Cluster supports PostgreSQL databases"
    CLUSTER_SUPPORTS_POSTGRESQL_DATABASE_USERS = (
        "Cluster supports PostgreSQL database users"
    )
    CLUSTER_SUPPORTS_NGINX_VIRTUAL_HOSTS = "Cluster supports nginx virtual hosts"
    CLUSTER_SUPPORTS_APACHE_VIRTUAL_HOSTS = "Cluster supports Apache virtual hosts"
    CLUSTER_SUPPORTS_NGINX_CUSTOM_CONFIGS = "Cluster supports nginx custom configs"
    CLUSTER_SUPPORTS_NGINX_CUSTOM_CONFIG_SNIPPETS = (
        "Cluster supports nginx custom config snippets"
    )
    CLUSTER_SUPPORTS_APACHE_CUSTOM_CONFIG_SNIPPETS = (
        "Cluster supports Apache custom config snippets"
    )
    CLUSTER_SUPPORTS_URL_REDIRECTS = "Cluster supports URL redirects"
    CLUSTER_SUPPORTS_HTPASSWD_FILES = "Cluster supports htpasswd files"
    CLUSTER_SUPPORTS_MAIL_DOMAINS = "Cluster supports mail domains"
    CLUSTER_SUPPORTS_MAIL_HOSTNAMES = "Cluster supports mail hostnames"
    CLUSTER_SUPPORTS_BORG_REPOSITORIES = "Cluster supports Borg repositories"
    CLUSTER_SUPPORTS_FTP_USERS = "Cluster supports FTP users"
    CLUSTER_SUPPORTS_FPM_POOLS = "Cluster supports FPM pools"
    CLUSTER_SUPPORTS_PASSENGER_APPS = "Cluster supports Passenger apps"
    CLUSTER_SUPPORTS_REDIS_INSTANCES = "Cluster supports Redis instances"
    CLUSTER_SUPPORTS_UNIX_USERS = "Cluster supports UNIX users"
    CLUSTER_SUPPORTS_FIREWALL_RULES = "Cluster supports firewall rules"
    CLUSTER_SUPPORTS_FIREWALL_GROUPS = "Cluster supports firewall groups"
    CLUSTER_SUPPORTS_MALDET_NODES = "Cluster supports maldet nodes"
    CLUSTER_SUPPORTS_DOCKER_NODES = "Cluster supports Docker nodes"
    CLUSTER_SUPPORTS_FFMPEG_NODES = "Cluster supports FFmpeg nodes"
    CLUSTER_SUPPORTS_GHOSTSCRIPT_NODES = "Cluster supports Ghostscript nodes"
    CLUSTER_SUPPORTS_LIBREOFFICE_NODES = "Cluster supports LibreOffice nodes"
    CLUSTER_SUPPORTS_PUPPETEER_NODES = "Cluster supports Puppeteer nodes"
    CLUSTER_SUPPORTS_CLAMAV_NODES = "Cluster supports ClamAV nodes"
    CLUSTER_SUPPORTS_GNU_MAILUTILS_NODES = "Cluster supports GNU Mailutils nodes"
    CLUSTER_SUPPORTS_WKHTMLTOPDF_NODES = "Cluster supports wkhtmltopdf nodes"
    CLUSTER_SUPPORTS_IMAGEMAGICK_NODES = "Cluster supports ImageMagick nodes"
    CLUSTER_SUPPORTS_HAPROXY_NODES = "Cluster supports HAProxy nodes"
    CLUSTER_SUPPORTS_PROFTPD_NODES = "Cluster supports ProFTPD nodes"
    CLUSTER_SUPPORTS_DOVECOT_NODES = "Cluster supports Dovecot nodes"
    CLUSTER_SUPPORTS_ADMIN_NODES = "Cluster supports admin nodes"
    CLUSTER_SUPPORTS_APACHE_NODES = "Cluster supports Apache nodes"
    CLUSTER_SUPPORTS_NGINX_NODES = "Cluster supports nginx nodes"
    CLUSTER_SUPPORTS_FAST_REDIRECT_NODES = "Cluster supports Fast Redirect nodes"
    CLUSTER_SUPPORTS_MARIADB_NODES = "Cluster supports MariaDB nodes"
    CLUSTER_SUPPORTS_POSTGRESQL_NODES = "Cluster supports PostgreSQL nodes"
    CLUSTER_SUPPORTS_PHP_NODES = "Cluster supports PHP nodes"
    CLUSTER_SUPPORTS_COMPOSER_NODES = "Cluster supports Composer nodes"
    CLUSTER_SUPPORTS_WP_CLI_NODES = "Cluster supports WP-CLI nodes"
    CLUSTER_SUPPORTS_NODEJS_NODES = "Cluster supports NodeJS nodes"
    CLUSTER_SUPPORTS_PASSENGER_NODES = "Cluster supports Passenger nodes"
    CLUSTER_SUPPORTS_BORG_NODES = "Cluster supports Borg nodes"
    CLUSTER_SUPPORTS_KERNELCARE_NODES = "Cluster supports KernelCare nodes"
    CLUSTER_SUPPORTS_NEW_RELIC_NODES = "Cluster supports New Relic nodes"
    CLUSTER_SUPPORTS_REDIS_NODES = "Cluster supports Redis nodes"
    CLUSTER_SUPPORTS_MEILISEARCH_NODES = "Cluster supports Meilisearch nodes"
    CLUSTER_SUPPORTS_GRAFANA_NODES = "Cluster supports Grafana nodes"
    CLUSTER_SUPPORTS_SINGLESTORE_NODES = "Cluster supports SingleStore nodes"
    CLUSTER_SUPPORTS_ELASTICSEARCH_NODES = "Cluster supports Elasticsearch nodes"
    CLUSTER_SUPPORTS_RABBITMQ_NODES = "Cluster supports RabbitMQ nodes"
    CLUSTER_SUPPORTS_METABASE_NODES = "Cluster supports Metabase nodes"
    UNIX_USER_SUPPORTS_VIRTUAL_HOSTS = "UNIX user supports virtual hosts"
    UNIX_USER_SUPPORTS_MAIL_DOMAINS = "UNIX user supports mail domains"
    UNIX_USER_SUPPORTS_BORG_REPOSITORIES = "UNIX user supports Borg repositories"


NestedPathsDict.update_forward_refs()
CompositeSpecificationSatisfyResult.update_forward_refs()
CompositeSpecificationSatisfyResultResource.update_forward_refs()
