r'''
# `tfe_opa_version`

Refer to the Terraform Registry for docs: [`tfe_opa_version`](https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class OpaVersion(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.opaVersion.OpaVersion",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version tfe_opa_version}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        version: builtins.str,
        archs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OpaVersionArchs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        beta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deprecated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deprecated_reason: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        official: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sha: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version tfe_opa_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#version OpaVersion#version}.
        :param archs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#archs OpaVersion#archs}.
        :param beta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#beta OpaVersion#beta}.
        :param deprecated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated OpaVersion#deprecated}.
        :param deprecated_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated_reason OpaVersion#deprecated_reason}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#enabled OpaVersion#enabled}.
        :param official: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#official OpaVersion#official}.
        :param sha: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#sha OpaVersion#sha}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#url OpaVersion#url}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93fef06fb8aa212fc1fce77e3f0db827f473d6ed238a4ce7cac97cb2f726d864)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = OpaVersionConfig(
            version=version,
            archs=archs,
            beta=beta,
            deprecated=deprecated,
            deprecated_reason=deprecated_reason,
            enabled=enabled,
            official=official,
            sha=sha,
            url=url,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a OpaVersion resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OpaVersion to import.
        :param import_from_id: The id of the existing OpaVersion that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OpaVersion to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6954d9835244f41108d26d954859acc537dbc6fa73db3a863da9533ac92c2f87)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putArchs")
    def put_archs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OpaVersionArchs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1436d093ad9c4286d8466d69b515936236831ec17ad7f530555e0888d0ba9a97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putArchs", [value]))

    @jsii.member(jsii_name="resetArchs")
    def reset_archs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArchs", []))

    @jsii.member(jsii_name="resetBeta")
    def reset_beta(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBeta", []))

    @jsii.member(jsii_name="resetDeprecated")
    def reset_deprecated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecated", []))

    @jsii.member(jsii_name="resetDeprecatedReason")
    def reset_deprecated_reason(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeprecatedReason", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetOfficial")
    def reset_official(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOfficial", []))

    @jsii.member(jsii_name="resetSha")
    def reset_sha(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSha", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="archs")
    def archs(self) -> "OpaVersionArchsList":
        return typing.cast("OpaVersionArchsList", jsii.get(self, "archs"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="archsInput")
    def archs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OpaVersionArchs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OpaVersionArchs"]]], jsii.get(self, "archsInput"))

    @builtins.property
    @jsii.member(jsii_name="betaInput")
    def beta_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "betaInput"))

    @builtins.property
    @jsii.member(jsii_name="deprecatedInput")
    def deprecated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deprecatedInput"))

    @builtins.property
    @jsii.member(jsii_name="deprecatedReasonInput")
    def deprecated_reason_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deprecatedReasonInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="officialInput")
    def official_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "officialInput"))

    @builtins.property
    @jsii.member(jsii_name="shaInput")
    def sha_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shaInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="beta")
    def beta(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "beta"))

    @beta.setter
    def beta(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa8c564faeffde4f9d9f5104271c50f5c307c23844134f1ca29ff8cb02dd68b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "beta", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deprecated")
    def deprecated(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deprecated"))

    @deprecated.setter
    def deprecated(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fc29171101a0e19ee8bcb177c9633e3d63954461cbc18d4e39fdab665962bec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deprecated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deprecatedReason")
    def deprecated_reason(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deprecatedReason"))

    @deprecated_reason.setter
    def deprecated_reason(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f75fe2e655ec811a0a6f54e0c407b2c11b8574ed3ce9e81179e2b0ef9e8ff6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deprecatedReason", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb7cd9e2b528a62b0d51186b8199f08619aabdb9b32d277cac22e955480b9f2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="official")
    def official(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "official"))

    @official.setter
    def official(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf52171cb5219d3b10e5444f0da333226db3a6625fce5d5a64edafa2b29237a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "official", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sha")
    def sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha"))

    @sha.setter
    def sha(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b7c526228e5a4b048bc4f87122c91b2b1033ff12807570bfc90125bac0e8668)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sha", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6497845032ac4d0a8875b5f931ca4c3c1391e8f8d6e9d3cfe5810038027b1a58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17e9dd4a19742e725f5ac9a76553a083b7b7a4fcd3edfd7b39020f90f3ae8c0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.opaVersion.OpaVersionArchs",
    jsii_struct_bases=[],
    name_mapping={"arch": "arch", "os": "os", "sha": "sha", "url": "url"},
)
class OpaVersionArchs:
    def __init__(
        self,
        *,
        arch: builtins.str,
        os: builtins.str,
        sha: builtins.str,
        url: builtins.str,
    ) -> None:
        '''
        :param arch: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#arch OpaVersion#arch}.
        :param os: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#os OpaVersion#os}.
        :param sha: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#sha OpaVersion#sha}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#url OpaVersion#url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81448832c823fd0d2a661a04ecf2388c93a08116f62fac16eb5a3c326d30c35d)
            check_type(argname="argument arch", value=arch, expected_type=type_hints["arch"])
            check_type(argname="argument os", value=os, expected_type=type_hints["os"])
            check_type(argname="argument sha", value=sha, expected_type=type_hints["sha"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "arch": arch,
            "os": os,
            "sha": sha,
            "url": url,
        }

    @builtins.property
    def arch(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#arch OpaVersion#arch}.'''
        result = self._values.get("arch")
        assert result is not None, "Required property 'arch' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def os(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#os OpaVersion#os}.'''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sha(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#sha OpaVersion#sha}.'''
        result = self._values.get("sha")
        assert result is not None, "Required property 'sha' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#url OpaVersion#url}.'''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpaVersionArchs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OpaVersionArchsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.opaVersion.OpaVersionArchsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a20597d048ae1f818279d1fb5243424f2c46e63adf6ea87e8769e8320eb40c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OpaVersionArchsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e002f485ef86d397ec7c04f58103c53195abe606723da2091b786b89051df28)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OpaVersionArchsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83d0948ae56a7546dba3dc8f32ac1c08b96f5eb7a93a0c2d9e14be6819d06915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af2d2387356217c3cbcbe24b8185e3e334af3451950544377e51acfaa496fb2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d07f918313773a8f57d9626afba02701e6347351daab4a601a0d8913fba73a05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f9c9fdf14122262977bb644216071055f5ef099018c59554f01e6d913b6623)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OpaVersionArchsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.opaVersion.OpaVersionArchsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46916a9a48f6090fa3a6c605253be1e6cb6cde2cfda84b2407eab69c28f9c430)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="archInput")
    def arch_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "archInput"))

    @builtins.property
    @jsii.member(jsii_name="osInput")
    def os_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "osInput"))

    @builtins.property
    @jsii.member(jsii_name="shaInput")
    def sha_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "shaInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="arch")
    def arch(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arch"))

    @arch.setter
    def arch(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c33bff880b54b7dbc6d3a029df4a8f02b23ab7743741a7d898b0faab6c03da1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="os")
    def os(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "os"))

    @os.setter
    def os(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38a6e2df724747951be4ef33715e9eaed790d35a898658e6032402b15461772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "os", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sha")
    def sha(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha"))

    @sha.setter
    def sha(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a26e4e3fd7609f7f56ac56402417b5366fddc6b4661c5d2099be6c2845b5cb25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sha", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fac76e07689b8f929c333276f3aa0879bfb5ffade018e97d3feaefe19ab1f181)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OpaVersionArchs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OpaVersionArchs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OpaVersionArchs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ddca79110f39faad0415bd64bbe5026a674fae6ef517311a108bccb3d3af838)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.opaVersion.OpaVersionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "version": "version",
        "archs": "archs",
        "beta": "beta",
        "deprecated": "deprecated",
        "deprecated_reason": "deprecatedReason",
        "enabled": "enabled",
        "official": "official",
        "sha": "sha",
        "url": "url",
    },
)
class OpaVersionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        version: builtins.str,
        archs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OpaVersionArchs, typing.Dict[builtins.str, typing.Any]]]]] = None,
        beta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deprecated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        deprecated_reason: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        official: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sha: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#version OpaVersion#version}.
        :param archs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#archs OpaVersion#archs}.
        :param beta: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#beta OpaVersion#beta}.
        :param deprecated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated OpaVersion#deprecated}.
        :param deprecated_reason: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated_reason OpaVersion#deprecated_reason}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#enabled OpaVersion#enabled}.
        :param official: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#official OpaVersion#official}.
        :param sha: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#sha OpaVersion#sha}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#url OpaVersion#url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6c820c6d219f1b8d853fc47ed1c0ed5567392600632ae81be952706808a81b4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument archs", value=archs, expected_type=type_hints["archs"])
            check_type(argname="argument beta", value=beta, expected_type=type_hints["beta"])
            check_type(argname="argument deprecated", value=deprecated, expected_type=type_hints["deprecated"])
            check_type(argname="argument deprecated_reason", value=deprecated_reason, expected_type=type_hints["deprecated_reason"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument official", value=official, expected_type=type_hints["official"])
            check_type(argname="argument sha", value=sha, expected_type=type_hints["sha"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if archs is not None:
            self._values["archs"] = archs
        if beta is not None:
            self._values["beta"] = beta
        if deprecated is not None:
            self._values["deprecated"] = deprecated
        if deprecated_reason is not None:
            self._values["deprecated_reason"] = deprecated_reason
        if enabled is not None:
            self._values["enabled"] = enabled
        if official is not None:
            self._values["official"] = official
        if sha is not None:
            self._values["sha"] = sha
        if url is not None:
            self._values["url"] = url

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#version OpaVersion#version}.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def archs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#archs OpaVersion#archs}.'''
        result = self._values.get("archs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]], result)

    @builtins.property
    def beta(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#beta OpaVersion#beta}.'''
        result = self._values.get("beta")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deprecated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated OpaVersion#deprecated}.'''
        result = self._values.get("deprecated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def deprecated_reason(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#deprecated_reason OpaVersion#deprecated_reason}.'''
        result = self._values.get("deprecated_reason")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#enabled OpaVersion#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def official(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#official OpaVersion#official}.'''
        result = self._values.get("official")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sha(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#sha OpaVersion#sha}.'''
        result = self._values.get("sha")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/opa_version#url OpaVersion#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OpaVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "OpaVersion",
    "OpaVersionArchs",
    "OpaVersionArchsList",
    "OpaVersionArchsOutputReference",
    "OpaVersionConfig",
]

publication.publish()

def _typecheckingstub__93fef06fb8aa212fc1fce77e3f0db827f473d6ed238a4ce7cac97cb2f726d864(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    version: builtins.str,
    archs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OpaVersionArchs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    beta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deprecated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deprecated_reason: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    official: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sha: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6954d9835244f41108d26d954859acc537dbc6fa73db3a863da9533ac92c2f87(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1436d093ad9c4286d8466d69b515936236831ec17ad7f530555e0888d0ba9a97(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OpaVersionArchs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa8c564faeffde4f9d9f5104271c50f5c307c23844134f1ca29ff8cb02dd68b2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fc29171101a0e19ee8bcb177c9633e3d63954461cbc18d4e39fdab665962bec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f75fe2e655ec811a0a6f54e0c407b2c11b8574ed3ce9e81179e2b0ef9e8ff6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb7cd9e2b528a62b0d51186b8199f08619aabdb9b32d277cac22e955480b9f2a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf52171cb5219d3b10e5444f0da333226db3a6625fce5d5a64edafa2b29237a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b7c526228e5a4b048bc4f87122c91b2b1033ff12807570bfc90125bac0e8668(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6497845032ac4d0a8875b5f931ca4c3c1391e8f8d6e9d3cfe5810038027b1a58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17e9dd4a19742e725f5ac9a76553a083b7b7a4fcd3edfd7b39020f90f3ae8c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81448832c823fd0d2a661a04ecf2388c93a08116f62fac16eb5a3c326d30c35d(
    *,
    arch: builtins.str,
    os: builtins.str,
    sha: builtins.str,
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a20597d048ae1f818279d1fb5243424f2c46e63adf6ea87e8769e8320eb40c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e002f485ef86d397ec7c04f58103c53195abe606723da2091b786b89051df28(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83d0948ae56a7546dba3dc8f32ac1c08b96f5eb7a93a0c2d9e14be6819d06915(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af2d2387356217c3cbcbe24b8185e3e334af3451950544377e51acfaa496fb2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d07f918313773a8f57d9626afba02701e6347351daab4a601a0d8913fba73a05(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f9c9fdf14122262977bb644216071055f5ef099018c59554f01e6d913b6623(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OpaVersionArchs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46916a9a48f6090fa3a6c605253be1e6cb6cde2cfda84b2407eab69c28f9c430(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c33bff880b54b7dbc6d3a029df4a8f02b23ab7743741a7d898b0faab6c03da1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38a6e2df724747951be4ef33715e9eaed790d35a898658e6032402b15461772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a26e4e3fd7609f7f56ac56402417b5366fddc6b4661c5d2099be6c2845b5cb25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fac76e07689b8f929c333276f3aa0879bfb5ffade018e97d3feaefe19ab1f181(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ddca79110f39faad0415bd64bbe5026a674fae6ef517311a108bccb3d3af838(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OpaVersionArchs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c820c6d219f1b8d853fc47ed1c0ed5567392600632ae81be952706808a81b4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    version: builtins.str,
    archs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OpaVersionArchs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    beta: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deprecated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    deprecated_reason: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    official: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sha: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
