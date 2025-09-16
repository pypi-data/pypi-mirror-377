r'''
# `tfe_workspace_settings`

Refer to the Terraform Registry for docs: [`tfe_workspace_settings`](https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings).
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


class WorkspaceSettings(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.workspaceSettings.WorkspaceSettings",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings tfe_workspace_settings}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        workspace_id: builtins.str,
        agent_pool_id: typing.Optional[builtins.str] = None,
        assessments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_apply: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        effective_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_mode: typing.Optional[builtins.str] = None,
        global_remote_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        remote_state_consumer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings tfe_workspace_settings} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#workspace_id WorkspaceSettings#workspace_id}.
        :param agent_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#agent_pool_id WorkspaceSettings#agent_pool_id}.
        :param assessments_enabled: If set to true, assessments will be enabled for the workspace. This includes drift and continuous validation checks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#assessments_enabled WorkspaceSettings#assessments_enabled}
        :param auto_apply: If set to false a human will have to manually confirm a plan in HCP Terraform's UI to start an apply. If set to true, this resource will be automatically applied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#auto_apply WorkspaceSettings#auto_apply}
        :param description: A description of the workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#description WorkspaceSettings#description}
        :param effective_tags: A map of all key-value tags set on the workspace (includes inheritted tags). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#effective_tags WorkspaceSettings#effective_tags}
        :param execution_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#execution_mode WorkspaceSettings#execution_mode}.
        :param global_remote_state: Whether the workspace allows all workspaces in the organization to access its state data during runs. If false, then only workspaces defined in ``remote_state_consumer_ids`` can access its state. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#global_remote_state WorkspaceSettings#global_remote_state}
        :param remote_state_consumer_ids: The set of workspace IDs set as explicit remote state consumers for the given workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#remote_state_consumer_ids WorkspaceSettings#remote_state_consumer_ids}
        :param tags: A map of key-value tags to add to the workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#tags WorkspaceSettings#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd34157c0c2f9da54af67806d57a267b0ffeb1f46ab5286500e5cbb7f27e7d2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = WorkspaceSettingsConfig(
            workspace_id=workspace_id,
            agent_pool_id=agent_pool_id,
            assessments_enabled=assessments_enabled,
            auto_apply=auto_apply,
            description=description,
            effective_tags=effective_tags,
            execution_mode=execution_mode,
            global_remote_state=global_remote_state,
            remote_state_consumer_ids=remote_state_consumer_ids,
            tags=tags,
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
        '''Generates CDKTF code for importing a WorkspaceSettings resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the WorkspaceSettings to import.
        :param import_from_id: The id of the existing WorkspaceSettings that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the WorkspaceSettings to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94b97e3fd734e524115712c8ae0d1323a845185bcc406c110e8a17d159130b85)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAgentPoolId")
    def reset_agent_pool_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentPoolId", []))

    @jsii.member(jsii_name="resetAssessmentsEnabled")
    def reset_assessments_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssessmentsEnabled", []))

    @jsii.member(jsii_name="resetAutoApply")
    def reset_auto_apply(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoApply", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEffectiveTags")
    def reset_effective_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEffectiveTags", []))

    @jsii.member(jsii_name="resetExecutionMode")
    def reset_execution_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExecutionMode", []))

    @jsii.member(jsii_name="resetGlobalRemoteState")
    def reset_global_remote_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlobalRemoteState", []))

    @jsii.member(jsii_name="resetRemoteStateConsumerIds")
    def reset_remote_state_consumer_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoteStateConsumerIds", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="overwrites")
    def overwrites(self) -> "WorkspaceSettingsOverwritesList":
        return typing.cast("WorkspaceSettingsOverwritesList", jsii.get(self, "overwrites"))

    @builtins.property
    @jsii.member(jsii_name="agentPoolIdInput")
    def agent_pool_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentPoolIdInput"))

    @builtins.property
    @jsii.member(jsii_name="assessmentsEnabledInput")
    def assessments_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "assessmentsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="autoApplyInput")
    def auto_apply_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoApplyInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="effectiveTagsInput")
    def effective_tags_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "effectiveTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="executionModeInput")
    def execution_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "executionModeInput"))

    @builtins.property
    @jsii.member(jsii_name="globalRemoteStateInput")
    def global_remote_state_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "globalRemoteStateInput"))

    @builtins.property
    @jsii.member(jsii_name="remoteStateConsumerIdsInput")
    def remote_state_consumer_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "remoteStateConsumerIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="workspaceIdInput")
    def workspace_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workspaceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="agentPoolId")
    def agent_pool_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentPoolId"))

    @agent_pool_id.setter
    def agent_pool_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e0adf5ce961db1845c4373d8cb9a50b3dc0115e344f588e5bd845b0f329eabc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentPoolId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="assessmentsEnabled")
    def assessments_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "assessmentsEnabled"))

    @assessments_enabled.setter
    def assessments_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc87eaaac9b946ec39a1d60b76f452f132f8f91309ebd6ace131fe4730c1928a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assessmentsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoApply")
    def auto_apply(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoApply"))

    @auto_apply.setter
    def auto_apply(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa2cdb1ce0e7159a890f758e3e1aed8bcad563eef19b34a911bbdbb5fd3b1596)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoApply", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b84552c398f934d578f775cc1fca25e25e3762a4add47cd10c0a2e73c81c619)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="effectiveTags")
    def effective_tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "effectiveTags"))

    @effective_tags.setter
    def effective_tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e83fb760e9593e7f707522e24b5087da840ebe08e4e73a733a6de19b98879c3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "effectiveTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="executionMode")
    def execution_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "executionMode"))

    @execution_mode.setter
    def execution_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3159aac8910abd8f1d56aaf86ae643d18c993c51f4949e588ab1764124c9c11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "executionMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="globalRemoteState")
    def global_remote_state(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "globalRemoteState"))

    @global_remote_state.setter
    def global_remote_state(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e3bf59f062f0a62bd31b266dc659a38b0c9c6cd6a595b0987a606e40de486be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "globalRemoteState", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="remoteStateConsumerIds")
    def remote_state_consumer_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "remoteStateConsumerIds"))

    @remote_state_consumer_ids.setter
    def remote_state_consumer_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df62359d4dead729106999b634f2e30ea34bfd2e4b3a12a4119a128b2e39a792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "remoteStateConsumerIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b781e69ac6e88890d393031422bb8520e0e6e003d1aafe430d9f47b1611ea46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workspaceId")
    def workspace_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workspaceId"))

    @workspace_id.setter
    def workspace_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd78a5545e03634439fb91d3299303a778837b846773344296ba732ebdb44966)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workspaceId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.workspaceSettings.WorkspaceSettingsConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "workspace_id": "workspaceId",
        "agent_pool_id": "agentPoolId",
        "assessments_enabled": "assessmentsEnabled",
        "auto_apply": "autoApply",
        "description": "description",
        "effective_tags": "effectiveTags",
        "execution_mode": "executionMode",
        "global_remote_state": "globalRemoteState",
        "remote_state_consumer_ids": "remoteStateConsumerIds",
        "tags": "tags",
    },
)
class WorkspaceSettingsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        workspace_id: builtins.str,
        agent_pool_id: typing.Optional[builtins.str] = None,
        assessments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_apply: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        effective_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_mode: typing.Optional[builtins.str] = None,
        global_remote_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        remote_state_consumer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param workspace_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#workspace_id WorkspaceSettings#workspace_id}.
        :param agent_pool_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#agent_pool_id WorkspaceSettings#agent_pool_id}.
        :param assessments_enabled: If set to true, assessments will be enabled for the workspace. This includes drift and continuous validation checks. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#assessments_enabled WorkspaceSettings#assessments_enabled}
        :param auto_apply: If set to false a human will have to manually confirm a plan in HCP Terraform's UI to start an apply. If set to true, this resource will be automatically applied. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#auto_apply WorkspaceSettings#auto_apply}
        :param description: A description of the workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#description WorkspaceSettings#description}
        :param effective_tags: A map of all key-value tags set on the workspace (includes inheritted tags). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#effective_tags WorkspaceSettings#effective_tags}
        :param execution_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#execution_mode WorkspaceSettings#execution_mode}.
        :param global_remote_state: Whether the workspace allows all workspaces in the organization to access its state data during runs. If false, then only workspaces defined in ``remote_state_consumer_ids`` can access its state. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#global_remote_state WorkspaceSettings#global_remote_state}
        :param remote_state_consumer_ids: The set of workspace IDs set as explicit remote state consumers for the given workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#remote_state_consumer_ids WorkspaceSettings#remote_state_consumer_ids}
        :param tags: A map of key-value tags to add to the workspace. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#tags WorkspaceSettings#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb4109f6d74657b37c158036838bb38bda69de50e8b038979b19407e7f545bb0)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument workspace_id", value=workspace_id, expected_type=type_hints["workspace_id"])
            check_type(argname="argument agent_pool_id", value=agent_pool_id, expected_type=type_hints["agent_pool_id"])
            check_type(argname="argument assessments_enabled", value=assessments_enabled, expected_type=type_hints["assessments_enabled"])
            check_type(argname="argument auto_apply", value=auto_apply, expected_type=type_hints["auto_apply"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument effective_tags", value=effective_tags, expected_type=type_hints["effective_tags"])
            check_type(argname="argument execution_mode", value=execution_mode, expected_type=type_hints["execution_mode"])
            check_type(argname="argument global_remote_state", value=global_remote_state, expected_type=type_hints["global_remote_state"])
            check_type(argname="argument remote_state_consumer_ids", value=remote_state_consumer_ids, expected_type=type_hints["remote_state_consumer_ids"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "workspace_id": workspace_id,
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
        if agent_pool_id is not None:
            self._values["agent_pool_id"] = agent_pool_id
        if assessments_enabled is not None:
            self._values["assessments_enabled"] = assessments_enabled
        if auto_apply is not None:
            self._values["auto_apply"] = auto_apply
        if description is not None:
            self._values["description"] = description
        if effective_tags is not None:
            self._values["effective_tags"] = effective_tags
        if execution_mode is not None:
            self._values["execution_mode"] = execution_mode
        if global_remote_state is not None:
            self._values["global_remote_state"] = global_remote_state
        if remote_state_consumer_ids is not None:
            self._values["remote_state_consumer_ids"] = remote_state_consumer_ids
        if tags is not None:
            self._values["tags"] = tags

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
    def workspace_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#workspace_id WorkspaceSettings#workspace_id}.'''
        result = self._values.get("workspace_id")
        assert result is not None, "Required property 'workspace_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_pool_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#agent_pool_id WorkspaceSettings#agent_pool_id}.'''
        result = self._values.get("agent_pool_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assessments_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to true, assessments will be enabled for the workspace. This includes drift and continuous validation checks.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#assessments_enabled WorkspaceSettings#assessments_enabled}
        '''
        result = self._values.get("assessments_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_apply(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set to false a human will have to manually confirm a plan in HCP Terraform's UI to start an apply.

        If set to true, this resource will be automatically applied.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#auto_apply WorkspaceSettings#auto_apply}
        '''
        result = self._values.get("auto_apply")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A description of the workspace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#description WorkspaceSettings#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def effective_tags(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of all key-value tags set on the workspace (includes inheritted tags).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#effective_tags WorkspaceSettings#effective_tags}
        '''
        result = self._values.get("effective_tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def execution_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#execution_mode WorkspaceSettings#execution_mode}.'''
        result = self._values.get("execution_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def global_remote_state(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether the workspace allows all workspaces in the organization to access its state data during runs.

        If false, then only workspaces defined in ``remote_state_consumer_ids`` can access its state.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#global_remote_state WorkspaceSettings#global_remote_state}
        '''
        result = self._values.get("global_remote_state")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def remote_state_consumer_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The set of workspace IDs set as explicit remote state consumers for the given workspace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#remote_state_consumer_ids WorkspaceSettings#remote_state_consumer_ids}
        '''
        result = self._values.get("remote_state_consumer_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of key-value tags to add to the workspace.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.69.0/docs/resources/workspace_settings#tags WorkspaceSettings#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.workspaceSettings.WorkspaceSettingsOverwrites",
    jsii_struct_bases=[],
    name_mapping={},
)
class WorkspaceSettingsOverwrites:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "WorkspaceSettingsOverwrites(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class WorkspaceSettingsOverwritesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.workspaceSettings.WorkspaceSettingsOverwritesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc458a82138391660c4834d8e04dd6cf67a9f9f5e68dd16eaca63b73cf6c3127)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "WorkspaceSettingsOverwritesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e593880b43087c6088d1807e374bf3b9b5da0bc39bbe8ac3c6bbd2543ba2828)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("WorkspaceSettingsOverwritesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df00379447be7539bf34e0f0e9426b019b23b186e4047f2e2b7f25caefd1c4f0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__064e8f92b4b0694bb0cdc7555a0ef2f04399c3cf9780f4f1f0fff3c0c0bd3b74)
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
            type_hints = typing.get_type_hints(_typecheckingstub__667fe6d442dfb87ce1415a9e0cb89ab10fac9bba62c8d98b9292534fc85609d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class WorkspaceSettingsOverwritesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.workspaceSettings.WorkspaceSettingsOverwritesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4acaa31d972b5aefedb11eb29a21bd47aa0392790bc37816eec4fd298bfd9ce9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="agentPool")
    def agent_pool(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "agentPool"))

    @builtins.property
    @jsii.member(jsii_name="executionMode")
    def execution_mode(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "executionMode"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[WorkspaceSettingsOverwrites]:
        return typing.cast(typing.Optional[WorkspaceSettingsOverwrites], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[WorkspaceSettingsOverwrites],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6a0d52095841a592c8380a76ccfa71084775b91380ac8a31b19078dea6ca6e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "WorkspaceSettings",
    "WorkspaceSettingsConfig",
    "WorkspaceSettingsOverwrites",
    "WorkspaceSettingsOverwritesList",
    "WorkspaceSettingsOverwritesOutputReference",
]

publication.publish()

def _typecheckingstub__efd34157c0c2f9da54af67806d57a267b0ffeb1f46ab5286500e5cbb7f27e7d2(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    workspace_id: builtins.str,
    agent_pool_id: typing.Optional[builtins.str] = None,
    assessments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_apply: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    effective_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    execution_mode: typing.Optional[builtins.str] = None,
    global_remote_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    remote_state_consumer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
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

def _typecheckingstub__94b97e3fd734e524115712c8ae0d1323a845185bcc406c110e8a17d159130b85(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e0adf5ce961db1845c4373d8cb9a50b3dc0115e344f588e5bd845b0f329eabc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc87eaaac9b946ec39a1d60b76f452f132f8f91309ebd6ace131fe4730c1928a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa2cdb1ce0e7159a890f758e3e1aed8bcad563eef19b34a911bbdbb5fd3b1596(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b84552c398f934d578f775cc1fca25e25e3762a4add47cd10c0a2e73c81c619(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e83fb760e9593e7f707522e24b5087da840ebe08e4e73a733a6de19b98879c3a(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3159aac8910abd8f1d56aaf86ae643d18c993c51f4949e588ab1764124c9c11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3bf59f062f0a62bd31b266dc659a38b0c9c6cd6a595b0987a606e40de486be(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df62359d4dead729106999b634f2e30ea34bfd2e4b3a12a4119a128b2e39a792(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b781e69ac6e88890d393031422bb8520e0e6e003d1aafe430d9f47b1611ea46(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd78a5545e03634439fb91d3299303a778837b846773344296ba732ebdb44966(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb4109f6d74657b37c158036838bb38bda69de50e8b038979b19407e7f545bb0(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    workspace_id: builtins.str,
    agent_pool_id: typing.Optional[builtins.str] = None,
    assessments_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_apply: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    effective_tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    execution_mode: typing.Optional[builtins.str] = None,
    global_remote_state: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    remote_state_consumer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc458a82138391660c4834d8e04dd6cf67a9f9f5e68dd16eaca63b73cf6c3127(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e593880b43087c6088d1807e374bf3b9b5da0bc39bbe8ac3c6bbd2543ba2828(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df00379447be7539bf34e0f0e9426b019b23b186e4047f2e2b7f25caefd1c4f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__064e8f92b4b0694bb0cdc7555a0ef2f04399c3cf9780f4f1f0fff3c0c0bd3b74(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__667fe6d442dfb87ce1415a9e0cb89ab10fac9bba62c8d98b9292534fc85609d4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4acaa31d972b5aefedb11eb29a21bd47aa0392790bc37816eec4fd298bfd9ce9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6a0d52095841a592c8380a76ccfa71084775b91380ac8a31b19078dea6ca6e5(
    value: typing.Optional[WorkspaceSettingsOverwrites],
) -> None:
    """Type checking stubs"""
    pass
