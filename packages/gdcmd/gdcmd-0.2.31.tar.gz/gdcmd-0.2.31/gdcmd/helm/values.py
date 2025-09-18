from enum import StrEnum
from typing import Optional, List, Dict, Any, Mapping, Literal
from deepmerge import always_merger
from pydantic import BaseModel, Field, ConfigDict, model_validator
from ruamel.yaml import YAML
from gdcmd.helm.values_parser import values_to_yaml


class Constants(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodeExporter: Literal["node-exporter"] = "node-exporter"
    prometheus: Literal["prometheus"] = "prometheus"
    server: Literal["server"] = "server"
    proxy: Literal["proxy"] = "proxy"
    dbExporter: Literal["db-exporter"] = "db-exporter"
    db: Literal["db"] = "db"
    sync: Literal["sync"] = "sync"
    link: Literal["link"] = "link"


class Deploy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    db: bool = Field(default=True, description="Should Postgres be deployed inside the cluster alongside each app")
    sync: bool = Field(default=True, description="Should SyncGrid app be deployed")
    link: bool = Field(default=True, description="Should LinkGrid app be deployed")
    systemd: bool = Field(default=True, description="Should Systemd service be deployed, only for local single-node deployments with podman kube play")
    keycloak: bool = Field(default=True, description="Should one Keycloak instance for all apps be deployed, together with a default realm")
    initializeKeycloak: bool = Field(default=False, description="Should Keycloak be initialized with default realm and roles, only if deploy.keycloak is true")
    prometheus: bool = Field(default=True, description="Should Prometheus monitoring services be deployed alongside each app")
    loadBalancerServices: bool = Field(default=True, description="Should LoadBalancer type services be created for apps, viable only for kubernetes deployments")
    development: bool = Field(default=True, description="Should development features be enabled")
    logging: bool = Field(default=True, description="Should logging with Promtail be enabled")


class Identity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    authority: str = Field(default="http://keycloak-pod:8080/realms/platform", description="Url to identity provider, defaults to locally deployed Keycloak instance")
    externalAuthority: str | None = Field(default="", description="Url where authority is reachable from outside, where anyone in network can reach it")


class RemoteWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(default="https://mimir.griddot.info/api/v1/push", description="")
    username: str = Field(default="mimir", description="")
    password: str = Field(default="Pk3mCDFTn8ri3dNLybAxSC", description="")
    write_relabel_configs: Optional[List[Dict[str, Any]]] = []
    basic_auth: Optional[Dict[str, str]] = {}


class Promtail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(default="loki.griddot.info/loki/api/v1/push", description="")
    username: str = Field(default="loki", description="")
    password: str = Field(default="h5xPqEXA3pQJHH8dHdr3", description="")


class Prometheus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nodeExporter: bool = Field(default=True, description="")
    databaseExporter: bool = Field(default=True, description="")
    cloudGrafana: bool = Field(default=True, description="Should remote write to Grafana Cloud be enabled")
    scrapeInterval: str = Field(default="5s", description="")
    evaluationInterval: str = Field(default="30m", description="")
    cloudGrafanaRemoteWrite: RemoteWrite = Field(default=RemoteWrite(), description="")
    additionalRemoteWrites: List[RemoteWrite] = Field(default=[], description="""
For example:
- url: https://url.to.remote.write/api/v1/push
 write_relabel_configs:
   - source_labels: [ __name__ ]
     action: keep
     regex: ".*"
 basic_auth:
   username: username
   password: pass""")


class Systemd(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deployFolder: str = Field(default="suite", description="This is folder on host from user home dir: e.g., \"suite\" for /home/<current-user>/suite")
    execCmd: str = Field(default="helm template -f values.yaml griddot/suite | podman kube play --replace --network suite -", description="")
    hostSshPort: int = Field(default=22, ge=1, le=65535, description="We connect to host from inside the container over ssh, this is host ssh port where sshd is listening")


class Postgres(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(default="user", description="Username of internally or externally deployed Postgres instance")
    password: str = Field(default="pass", description="Password of internally or externally deployed Postgres instance")
    host: str | None = Field(default="db", description="Host of externally deployed Postgres instance, defaults to internal deployment instance")
    sharedBuffer: str | None = Field(default="10GB", description="")


class AppHost(StrEnum):
    sync = "sync-pod"
    link = "link-pod"
    keycloak = "keycloak-pod"


class Keycloak(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adminUser: str = Field(default="admin", description="")
    adminPass: str = Field(default="admin", description="")
    adminEmail: str = Field(default="admin@mail.com", description="")
    postgres: Postgres = Field(default=Postgres(sharedBuffer=None, host=None), description="")
    host: AppHost = Field(default=AppHost.keycloak, description="Keycloak hostname, where it can be reached; NOTE: This cannot be changed! For info only")
    port: int = Field(default=8080, ge=1, le=65535, description="Change Keycloak host port if needed")


class Image(BaseModel):
    model_config = ConfigDict(extra="forbid")

    registry: str = Field(default="registry.gitlab.com/griddot/syncgrid", description="Point to your private registry where you pull the images")
    version: str = Field(default="v2025.1.745", description="")
    pullUser: str = Field(default="user", description="Username for private registry")
    pullPassword: str = Field(default="glpat-12345", description="Access token or password for private registry")


class App(BaseModel):
    model_config = ConfigDict(extra="forbid")

    host: AppHost = Field(default=AppHost.sync, description="App hostname, where it can be reached; NOTE: This cannot be changed! For info only")
    hostPortHttp: int = Field(default=1000, ge=1, le=65535, description="Change app host port for HTTP if needed")
    hostPortHttps: int = Field(default=0, ge=0, le=65535, description="Change app host port for HTTPS if needed. NOTE: common.requireHttps must be set to true to enable this port")
    licenceBase64: Optional[str] = Field(default="", description="Base64 encoded licence string, for development purposes only")
    dataGi: int = Field(default=20, ge=1, description="Size of persistent volume claim for app data in Gi")


class Sync(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image: Image = Field(default=Image(registry="registry.gitlab.com/griddot/syncgrid", version="v2025.1.875"), description="")
    postgres: Postgres = Field(default=Postgres(), description="")
    app: App = Field(default=App(hostPortHttp=7080, host=AppHost.sync), description="")


class KeyManagement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=True, description="")
    encryptionKey: str = Field(default="f5be9eb6d049882cba5ef743f98fbce6a96b2a30f063a516bb2f09ab02ec441c", description="")


class Link(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image: Image = Field(default=Image(registry="registry.gitlab.com/griddot/linkgrid", version="v2025.1.8"), description="")
    postgres: Postgres = Field(default=Postgres(), description="")
    app: App = Field(default=App(hostPortHttp=4080, host=AppHost.link), description="")
    keyManagement: KeyManagement = Field(default=KeyManagement(), description="")


class Common(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requireHttps: bool = Field(default=False, description="Set to true if you want to enforce HTTPS with self-signed certificates")
    identity: Identity = Field(default=Identity(), description="")
    certificatePassword: str = Field(default="z98M9gFsF7aJBn3s", description="Certificate password for self-signed certificates, used if common.requireHttps is true")
    reseller: str = Field(default="reseller-name", description="Reseller name")
    deploymentId: str = Field(default="deployment-id", description="Each deployment should have a unique id!")
    host: str = Field(default="localhost", description="Host name or ip where all apps are reachable from")
    timeZoneIdOverride: str | None = Field(default=None, description="If set, overrides the time zone id detected from the environment")


class ValuesYaml(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    consts: Constants = Field(default=Constants(), description="Fixed constants")
    deploy: Deploy = Field(default=Deploy(), description="\nDeployment configuration")
    common: Common = Field(default=Common(), description="\nCommon configuration")
    sync: Sync = Field(default=Sync(), description="\nSyncGrid configuration")
    link: Link = Field(default=Link(), description="\nLinkGrid configuration")
    prometheus: Prometheus = Field(default=Prometheus(), description="\nPrometheus configuration")
    promtail: Promtail = Field(default=Promtail(), description="\nPromtail configuration")
    systemd: Systemd = Field(default=Systemd(), description="\nSystemd configuration")
    keycloak: Keycloak = Field(default=Keycloak(), description="\nKeycloak configuration")

    @model_validator(mode="after")
    def validate_deployment_consistency(self) -> "ValuesYaml":
        """Validate that service configurations exist when deployment is enabled"""
        if self.deploy.prometheus and not self.prometheus:
            raise ValueError("Prometheus configuration required when deploy.prometheus is true")
        if self.deploy.keycloak and not self.keycloak:
            raise ValueError("Keycloak configuration required when deploy.keycloak is true")
        if self.deploy.sync and not self.sync:
            raise ValueError("SyncGrid configuration required when deploy.sync is true")
        if self.deploy.link and not self.link:
            raise ValueError("LinkGrid configuration required when deploy.link is true")
        if self.deploy.systemd and not self.systemd:
            raise ValueError("Systemd configuration required when deploy.systemd is true")

        if " " in self.common.deploymentId:
            raise ValueError("common.deploymentId cannot contain spaces")

        if self.common.requireHttps:
            if self.common.identity.authority.startswith("http://"):
                raise ValueError("common.identity.authority must start with https when common.requireHttps is true")
        else:
            if self.common.identity.authority.startswith("https"):
                raise ValueError("common.identity.authority must start with http when common.requireHttps is false")

        # Prometheus
        if self.prometheus.databaseExporter and not self.deploy.db:
            raise ValueError("deploy.db must be true to enable Prometheus databaseExporter")

        # App https port
        if self.sync.app.hostPortHttps > 0 and not self.common.requireHttps:
            raise ValueError("common.requireHttps must be true to enable SyncGrid HTTPS port")
        if self.link.app.hostPortHttps > 0 and not self.common.requireHttps:
            raise ValueError("common.requireHttps must be true to enable LinkGrid HTTPS port")
        return self

    @classmethod
    def from_str(cls, yaml_str: str) -> "ValuesYaml":
        data = YAML(typ='safe').load(yaml_str)
        return ValuesYaml.model_validate(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValuesYaml":
        return cls.model_validate(data)

    def to_str(self, exclude_none=False, exclude_defaults: bool = False, exclude_unset: bool = False, include: Mapping[str, Any] | set[str] | None = None, exclude: Mapping[str, Any] | set[str] | None = None, top_level_comment: str = "") -> str:
        yml = YAML()
        yml.representer.add_representer(AppHost, lambda dump, d: dump.represent_scalar("tag:yaml.org,2002:str", str(d)))
        return values_to_yaml(self, top_level_comment, yml, exclude_none, exclude_defaults, exclude_unset, include, exclude)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(by_alias=True)

    def merge(self, other: "ValuesYaml") -> "ValuesYaml":
        return always_merger.merge(self, other)

    def merge_dict(self, other: Dict[str, Any]) -> "ValuesYaml":
        return ValuesYaml.from_dict(always_merger.merge(self.to_dict(), other))
