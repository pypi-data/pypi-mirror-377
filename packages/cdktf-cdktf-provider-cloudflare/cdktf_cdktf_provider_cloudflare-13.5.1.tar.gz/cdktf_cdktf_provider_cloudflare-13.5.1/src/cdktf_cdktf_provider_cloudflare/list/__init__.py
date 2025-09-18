r'''
# `cloudflare_list`

Refer to the Terraform Registry for docs: [`cloudflare_list`](https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list).
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


class List(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.list.List",
):
    '''Represents a {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list cloudflare_list}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account_id: builtins.str,
        kind: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        items: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ListItems", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list cloudflare_list} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_id: The Account ID for this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#account_id List#account_id}
        :param kind: The type of the list. Each type supports specific list items (IP addresses, ASNs, hostnames or redirects). Available values: "ip", "redirect", "hostname", "asn". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#kind List#kind}
        :param name: An informative name for the list. Use this name in filter and rule expressions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#name List#name}
        :param description: An informative summary of the list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#description List#description}
        :param items: The items in the list. If set, this overwrites all items in the list. Do not use with ``cloudflare_list_item``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#items List#items}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524e2c7d37ad2ce42909cabda973d9e1d995b7f4970a151dffeb131cd179ffd6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ListConfig(
            account_id=account_id,
            kind=kind,
            name=name,
            description=description,
            items=items,
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
        '''Generates CDKTF code for importing a List resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the List to import.
        :param import_from_id: The id of the existing List that should be imported. Refer to the {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the List to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54470ea675ce3159046d6feaa4dea252895d724cd3988bdb00e3b512a0a8e141)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putItems")
    def put_items(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ListItems", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b296ca941bdd51038d5675e0964788f54ba79d4e0e79cdfc2d265fb814d7dd06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putItems", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetItems")
    def reset_items(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItems", []))

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
    @jsii.member(jsii_name="createdOn")
    def created_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdOn"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="items")
    def items(self) -> "ListItemsList":
        return typing.cast("ListItemsList", jsii.get(self, "items"))

    @builtins.property
    @jsii.member(jsii_name="modifiedOn")
    def modified_on(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modifiedOn"))

    @builtins.property
    @jsii.member(jsii_name="numItems")
    def num_items(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numItems"))

    @builtins.property
    @jsii.member(jsii_name="numReferencingFilters")
    def num_referencing_filters(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numReferencingFilters"))

    @builtins.property
    @jsii.member(jsii_name="accountIdInput")
    def account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="itemsInput")
    def items_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ListItems"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ListItems"]]], jsii.get(self, "itemsInput"))

    @builtins.property
    @jsii.member(jsii_name="kindInput")
    def kind_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "kindInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="accountId")
    def account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountId"))

    @account_id.setter
    def account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1752ad885ce059d786e1d5c2e40905e901c71f8b2ce95a352a725536478aa6bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb73b30d7da97952fc394c7b0bb3763ed7e889357a79df2bb20df110a0d411b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="kind")
    def kind(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "kind"))

    @kind.setter
    def kind(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e570c6b9e9c028fadd0332045d759175a31bc297ee7540c4204ebf9457763d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "kind", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9541ab37c34cf504c7a69b63e8a45b09565cd1bca6cf72ceb3400909fcacc703)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.list.ListConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_id": "accountId",
        "kind": "kind",
        "name": "name",
        "description": "description",
        "items": "items",
    },
)
class ListConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        account_id: builtins.str,
        kind: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        items: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ListItems", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_id: The Account ID for this resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#account_id List#account_id}
        :param kind: The type of the list. Each type supports specific list items (IP addresses, ASNs, hostnames or redirects). Available values: "ip", "redirect", "hostname", "asn". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#kind List#kind}
        :param name: An informative name for the list. Use this name in filter and rule expressions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#name List#name}
        :param description: An informative summary of the list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#description List#description}
        :param items: The items in the list. If set, this overwrites all items in the list. Do not use with ``cloudflare_list_item``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#items List#items}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11d2b96daec7d5ea9ecd7401f5efcd50ecbf8fbc0ca0176388cfc7a64f79cc5d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_id", value=account_id, expected_type=type_hints["account_id"])
            check_type(argname="argument kind", value=kind, expected_type=type_hints["kind"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument items", value=items, expected_type=type_hints["items"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "account_id": account_id,
            "kind": kind,
            "name": name,
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
        if description is not None:
            self._values["description"] = description
        if items is not None:
            self._values["items"] = items

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
    def account_id(self) -> builtins.str:
        '''The Account ID for this resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#account_id List#account_id}
        '''
        result = self._values.get("account_id")
        assert result is not None, "Required property 'account_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def kind(self) -> builtins.str:
        '''The type of the list.

        Each type supports specific list items (IP addresses, ASNs, hostnames or redirects).
        Available values: "ip", "redirect", "hostname", "asn".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#kind List#kind}
        '''
        result = self._values.get("kind")
        assert result is not None, "Required property 'kind' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''An informative name for the list. Use this name in filter and rule expressions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#name List#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''An informative summary of the list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#description List#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def items(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ListItems"]]]:
        '''The items in the list. If set, this overwrites all items in the list. Do not use with ``cloudflare_list_item``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#items List#items}
        '''
        result = self._values.get("items")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ListItems"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.list.ListItems",
    jsii_struct_bases=[],
    name_mapping={
        "asn": "asn",
        "comment": "comment",
        "hostname": "hostname",
        "ip": "ip",
        "redirect": "redirect",
    },
)
class ListItems:
    def __init__(
        self,
        *,
        asn: typing.Optional[jsii.Number] = None,
        comment: typing.Optional[builtins.str] = None,
        hostname: typing.Optional[typing.Union["ListItemsHostname", typing.Dict[builtins.str, typing.Any]]] = None,
        ip: typing.Optional[builtins.str] = None,
        redirect: typing.Optional[typing.Union["ListItemsRedirect", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param asn: A non-negative 32 bit integer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#asn List#asn}
        :param comment: An informative summary of the list item. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#comment List#comment}
        :param hostname: Valid characters for hostnames are ASCII(7) letters from a to z, the digits from 0 to 9, wildcards (*), and the hyphen (-). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#hostname List#hostname}
        :param ip: An IPv4 address, an IPv4 CIDR, an IPv6 address, or an IPv6 CIDR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#ip List#ip}
        :param redirect: The definition of the redirect. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#redirect List#redirect}
        '''
        if isinstance(hostname, dict):
            hostname = ListItemsHostname(**hostname)
        if isinstance(redirect, dict):
            redirect = ListItemsRedirect(**redirect)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee3b7370ced8b5b6b3d7cd8f4f46e3958bbb155bcde2583c60f4f87e6127e027)
            check_type(argname="argument asn", value=asn, expected_type=type_hints["asn"])
            check_type(argname="argument comment", value=comment, expected_type=type_hints["comment"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument ip", value=ip, expected_type=type_hints["ip"])
            check_type(argname="argument redirect", value=redirect, expected_type=type_hints["redirect"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if asn is not None:
            self._values["asn"] = asn
        if comment is not None:
            self._values["comment"] = comment
        if hostname is not None:
            self._values["hostname"] = hostname
        if ip is not None:
            self._values["ip"] = ip
        if redirect is not None:
            self._values["redirect"] = redirect

    @builtins.property
    def asn(self) -> typing.Optional[jsii.Number]:
        '''A non-negative 32 bit integer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#asn List#asn}
        '''
        result = self._values.get("asn")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def comment(self) -> typing.Optional[builtins.str]:
        '''An informative summary of the list item.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#comment List#comment}
        '''
        result = self._values.get("comment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hostname(self) -> typing.Optional["ListItemsHostname"]:
        '''Valid characters for hostnames are ASCII(7) letters from a to z, the digits from 0 to 9, wildcards (*), and the hyphen (-).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#hostname List#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional["ListItemsHostname"], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''An IPv4 address, an IPv4 CIDR, an IPv6 address, or an IPv6 CIDR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#ip List#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect(self) -> typing.Optional["ListItemsRedirect"]:
        '''The definition of the redirect.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#redirect List#redirect}
        '''
        result = self._values.get("redirect")
        return typing.cast(typing.Optional["ListItemsRedirect"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListItems(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsHostname",
    jsii_struct_bases=[],
    name_mapping={
        "url_hostname": "urlHostname",
        "exclude_exact_hostname": "excludeExactHostname",
    },
)
class ListItemsHostname:
    def __init__(
        self,
        *,
        url_hostname: builtins.str,
        exclude_exact_hostname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param url_hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#url_hostname List#url_hostname}.
        :param exclude_exact_hostname: Only applies to wildcard hostnames (e.g., *.example.com). When true (default), only subdomains are blocked. When false, both the root domain and subdomains are blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#exclude_exact_hostname List#exclude_exact_hostname}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afafc25338fa4fc5dfa9651b49c07d8387bb3f8e92bd26e4aac202e24c241d82)
            check_type(argname="argument url_hostname", value=url_hostname, expected_type=type_hints["url_hostname"])
            check_type(argname="argument exclude_exact_hostname", value=exclude_exact_hostname, expected_type=type_hints["exclude_exact_hostname"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "url_hostname": url_hostname,
        }
        if exclude_exact_hostname is not None:
            self._values["exclude_exact_hostname"] = exclude_exact_hostname

    @builtins.property
    def url_hostname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#url_hostname List#url_hostname}.'''
        result = self._values.get("url_hostname")
        assert result is not None, "Required property 'url_hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def exclude_exact_hostname(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Only applies to wildcard hostnames (e.g., *.example.com). When true (default), only subdomains are blocked. When false, both the root domain and subdomains are blocked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#exclude_exact_hostname List#exclude_exact_hostname}
        '''
        result = self._values.get("exclude_exact_hostname")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListItemsHostname(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ListItemsHostnameOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsHostnameOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28cb1b8350060e8eb1cf85fd0edde6f3d2c24eaaadb345e8197404a11a07ff5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExcludeExactHostname")
    def reset_exclude_exact_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExcludeExactHostname", []))

    @builtins.property
    @jsii.member(jsii_name="excludeExactHostnameInput")
    def exclude_exact_hostname_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "excludeExactHostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlHostnameInput")
    def url_hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlHostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="excludeExactHostname")
    def exclude_exact_hostname(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "excludeExactHostname"))

    @exclude_exact_hostname.setter
    def exclude_exact_hostname(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd5aaaff16c5ce7565fb86c08312a20f32d4db25effb9080df9e7b6eaa567255)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "excludeExactHostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urlHostname")
    def url_hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "urlHostname"))

    @url_hostname.setter
    def url_hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a9b00d781ee45194c74f4809f647ddfdf09883bcc513df2b20fa7b501a759c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urlHostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6db1cbe379d591886422fe74f784f8b2f877cca4a19b12ae5790ddda51a1b3c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ListItemsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4393aec9d8f32ba54654bb293ec44573cdb56b6de19515b1fed1fe6d554490a2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ListItemsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c34da65a0cb78f1d93d85c2630005d33aff90698c02e30993cfa016b4912ee5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ListItemsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d47889e1f47249196e64b61653ab060be7023a7538a7525d3ad8989534858d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__74198b6987edfe61370523dbf9fc7d24690dede2ee400a2c68bdf78846134aa1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__836161a62137689b919b86c8271bff6e587a322ecc9aacd25d8a83829ce8773b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ListItems]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ListItems]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ListItems]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026778b836b369015d734472b222c6766c72d7fc3ee1cbf148bd9d8bac47d17b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ListItemsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e9496a66d5911b8a5d93bdb5757d190fd01c94974ac39b3e0cd4df9efc98bde)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putHostname")
    def put_hostname(
        self,
        *,
        url_hostname: builtins.str,
        exclude_exact_hostname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param url_hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#url_hostname List#url_hostname}.
        :param exclude_exact_hostname: Only applies to wildcard hostnames (e.g., *.example.com). When true (default), only subdomains are blocked. When false, both the root domain and subdomains are blocked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#exclude_exact_hostname List#exclude_exact_hostname}
        '''
        value = ListItemsHostname(
            url_hostname=url_hostname, exclude_exact_hostname=exclude_exact_hostname
        )

        return typing.cast(None, jsii.invoke(self, "putHostname", [value]))

    @jsii.member(jsii_name="putRedirect")
    def put_redirect(
        self,
        *,
        source_url: builtins.str,
        target_url: builtins.str,
        include_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_path_suffix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_query_string: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        status_code: typing.Optional[jsii.Number] = None,
        subpath_matching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param source_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#source_url List#source_url}.
        :param target_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#target_url List#target_url}.
        :param include_subdomains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#include_subdomains List#include_subdomains}.
        :param preserve_path_suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_path_suffix List#preserve_path_suffix}.
        :param preserve_query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_query_string List#preserve_query_string}.
        :param status_code: Available values: 301, 302, 307, 308. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#status_code List#status_code}
        :param subpath_matching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#subpath_matching List#subpath_matching}.
        '''
        value = ListItemsRedirect(
            source_url=source_url,
            target_url=target_url,
            include_subdomains=include_subdomains,
            preserve_path_suffix=preserve_path_suffix,
            preserve_query_string=preserve_query_string,
            status_code=status_code,
            subpath_matching=subpath_matching,
        )

        return typing.cast(None, jsii.invoke(self, "putRedirect", [value]))

    @jsii.member(jsii_name="resetAsn")
    def reset_asn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAsn", []))

    @jsii.member(jsii_name="resetComment")
    def reset_comment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetComment", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetIp")
    def reset_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIp", []))

    @jsii.member(jsii_name="resetRedirect")
    def reset_redirect(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirect", []))

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> ListItemsHostnameOutputReference:
        return typing.cast(ListItemsHostnameOutputReference, jsii.get(self, "hostname"))

    @builtins.property
    @jsii.member(jsii_name="redirect")
    def redirect(self) -> "ListItemsRedirectOutputReference":
        return typing.cast("ListItemsRedirectOutputReference", jsii.get(self, "redirect"))

    @builtins.property
    @jsii.member(jsii_name="asnInput")
    def asn_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "asnInput"))

    @builtins.property
    @jsii.member(jsii_name="commentInput")
    def comment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commentInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="ipInput")
    def ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectInput")
    def redirect_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ListItemsRedirect"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ListItemsRedirect"]], jsii.get(self, "redirectInput"))

    @builtins.property
    @jsii.member(jsii_name="asn")
    def asn(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "asn"))

    @asn.setter
    def asn(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34f1d5032b26e590551c2157185b2ed0e829cb4cdde56ee4529f2d7c779e0730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "asn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="comment")
    def comment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "comment"))

    @comment.setter
    def comment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a23dc73c9ed3e8eef21a4704c12c85c24a2cf729d3a76acea0ec3498d2b2e506)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "comment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @ip.setter
    def ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47baf98e78840c1b4f90b473eb9e8ce271872f5df3b3c09b7102fd05adedcdab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ip", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItems]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItems]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItems]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__158c512e5253432e864c9e4b1ff7b30dd2e0ff26993d9ba311f222b0d056ecdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsRedirect",
    jsii_struct_bases=[],
    name_mapping={
        "source_url": "sourceUrl",
        "target_url": "targetUrl",
        "include_subdomains": "includeSubdomains",
        "preserve_path_suffix": "preservePathSuffix",
        "preserve_query_string": "preserveQueryString",
        "status_code": "statusCode",
        "subpath_matching": "subpathMatching",
    },
)
class ListItemsRedirect:
    def __init__(
        self,
        *,
        source_url: builtins.str,
        target_url: builtins.str,
        include_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_path_suffix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        preserve_query_string: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        status_code: typing.Optional[jsii.Number] = None,
        subpath_matching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param source_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#source_url List#source_url}.
        :param target_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#target_url List#target_url}.
        :param include_subdomains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#include_subdomains List#include_subdomains}.
        :param preserve_path_suffix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_path_suffix List#preserve_path_suffix}.
        :param preserve_query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_query_string List#preserve_query_string}.
        :param status_code: Available values: 301, 302, 307, 308. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#status_code List#status_code}
        :param subpath_matching: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#subpath_matching List#subpath_matching}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__121f2d5476076731519fe0692528af2981d6bc3fd4fca79e6908deb5d399b2e8)
            check_type(argname="argument source_url", value=source_url, expected_type=type_hints["source_url"])
            check_type(argname="argument target_url", value=target_url, expected_type=type_hints["target_url"])
            check_type(argname="argument include_subdomains", value=include_subdomains, expected_type=type_hints["include_subdomains"])
            check_type(argname="argument preserve_path_suffix", value=preserve_path_suffix, expected_type=type_hints["preserve_path_suffix"])
            check_type(argname="argument preserve_query_string", value=preserve_query_string, expected_type=type_hints["preserve_query_string"])
            check_type(argname="argument status_code", value=status_code, expected_type=type_hints["status_code"])
            check_type(argname="argument subpath_matching", value=subpath_matching, expected_type=type_hints["subpath_matching"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "source_url": source_url,
            "target_url": target_url,
        }
        if include_subdomains is not None:
            self._values["include_subdomains"] = include_subdomains
        if preserve_path_suffix is not None:
            self._values["preserve_path_suffix"] = preserve_path_suffix
        if preserve_query_string is not None:
            self._values["preserve_query_string"] = preserve_query_string
        if status_code is not None:
            self._values["status_code"] = status_code
        if subpath_matching is not None:
            self._values["subpath_matching"] = subpath_matching

    @builtins.property
    def source_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#source_url List#source_url}.'''
        result = self._values.get("source_url")
        assert result is not None, "Required property 'source_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#target_url List#target_url}.'''
        result = self._values.get("target_url")
        assert result is not None, "Required property 'target_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def include_subdomains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#include_subdomains List#include_subdomains}.'''
        result = self._values.get("include_subdomains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def preserve_path_suffix(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_path_suffix List#preserve_path_suffix}.'''
        result = self._values.get("preserve_path_suffix")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def preserve_query_string(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#preserve_query_string List#preserve_query_string}.'''
        result = self._values.get("preserve_query_string")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def status_code(self) -> typing.Optional[jsii.Number]:
        '''Available values: 301, 302, 307, 308.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#status_code List#status_code}
        '''
        result = self._values.get("status_code")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def subpath_matching(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/cloudflare/cloudflare/5.10.1/docs/resources/list#subpath_matching List#subpath_matching}.'''
        result = self._values.get("subpath_matching")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ListItemsRedirect(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ListItemsRedirectOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-cloudflare.list.ListItemsRedirectOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1ce9538d6bf6e87f7d7e0a3f88fec42feee2ba5e3c03f65d4999cd59c4c29de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIncludeSubdomains")
    def reset_include_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeSubdomains", []))

    @jsii.member(jsii_name="resetPreservePathSuffix")
    def reset_preserve_path_suffix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreservePathSuffix", []))

    @jsii.member(jsii_name="resetPreserveQueryString")
    def reset_preserve_query_string(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreserveQueryString", []))

    @jsii.member(jsii_name="resetStatusCode")
    def reset_status_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatusCode", []))

    @jsii.member(jsii_name="resetSubpathMatching")
    def reset_subpath_matching(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubpathMatching", []))

    @builtins.property
    @jsii.member(jsii_name="includeSubdomainsInput")
    def include_subdomains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeSubdomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="preservePathSuffixInput")
    def preserve_path_suffix_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "preservePathSuffixInput"))

    @builtins.property
    @jsii.member(jsii_name="preserveQueryStringInput")
    def preserve_query_string_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "preserveQueryStringInput"))

    @builtins.property
    @jsii.member(jsii_name="sourceUrlInput")
    def source_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sourceUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="statusCodeInput")
    def status_code_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "statusCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="subpathMatchingInput")
    def subpath_matching_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "subpathMatchingInput"))

    @builtins.property
    @jsii.member(jsii_name="targetUrlInput")
    def target_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="includeSubdomains")
    def include_subdomains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "includeSubdomains"))

    @include_subdomains.setter
    def include_subdomains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d705a4132aaf194d3c045f5a8a38e3d822270a18846e47ca66e8eb8e45615d98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeSubdomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preservePathSuffix")
    def preserve_path_suffix(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "preservePathSuffix"))

    @preserve_path_suffix.setter
    def preserve_path_suffix(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2779dca5b97f1b4b970e35d08f1068a48217be7dad33c3ba79e6ac5c1b2b59a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preservePathSuffix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preserveQueryString")
    def preserve_query_string(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "preserveQueryString"))

    @preserve_query_string.setter
    def preserve_query_string(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e237f409159c5b9512a0f967dcf597a776ea91f07f681e92db05bf306ee69d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preserveQueryString", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sourceUrl")
    def source_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sourceUrl"))

    @source_url.setter
    def source_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd2364eb064e5efa326a6d3907184f820843b98f757b26e98fff7adbe441c561)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sourceUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="statusCode")
    def status_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "statusCode"))

    @status_code.setter
    def status_code(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40aefa532f6346fc75f66d1fb505262351acf6c8f36242dd698e126a208f639e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "statusCode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subpathMatching")
    def subpath_matching(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "subpathMatching"))

    @subpath_matching.setter
    def subpath_matching(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__793e15f00cc69ec9ef181a1c7a5dd3a7b2e76dd9f5c1c13a3d39fea9f2aa6c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subpathMatching", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetUrl")
    def target_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetUrl"))

    @target_url.setter
    def target_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60c15af6cbe3b9bc510222228c7d47f9458d76e41578549b8d833ee40aec80fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsRedirect]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsRedirect]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsRedirect]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef6d034026ab2ac1895db9258f7fe0d0b8f483d519ba0bc62406e9da6e17079a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "List",
    "ListConfig",
    "ListItems",
    "ListItemsHostname",
    "ListItemsHostnameOutputReference",
    "ListItemsList",
    "ListItemsOutputReference",
    "ListItemsRedirect",
    "ListItemsRedirectOutputReference",
]

publication.publish()

def _typecheckingstub__524e2c7d37ad2ce42909cabda973d9e1d995b7f4970a151dffeb131cd179ffd6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account_id: builtins.str,
    kind: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    items: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ListItems, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__54470ea675ce3159046d6feaa4dea252895d724cd3988bdb00e3b512a0a8e141(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b296ca941bdd51038d5675e0964788f54ba79d4e0e79cdfc2d265fb814d7dd06(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ListItems, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1752ad885ce059d786e1d5c2e40905e901c71f8b2ce95a352a725536478aa6bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb73b30d7da97952fc394c7b0bb3763ed7e889357a79df2bb20df110a0d411b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e570c6b9e9c028fadd0332045d759175a31bc297ee7540c4204ebf9457763d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9541ab37c34cf504c7a69b63e8a45b09565cd1bca6cf72ceb3400909fcacc703(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11d2b96daec7d5ea9ecd7401f5efcd50ecbf8fbc0ca0176388cfc7a64f79cc5d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    account_id: builtins.str,
    kind: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    items: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ListItems, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee3b7370ced8b5b6b3d7cd8f4f46e3958bbb155bcde2583c60f4f87e6127e027(
    *,
    asn: typing.Optional[jsii.Number] = None,
    comment: typing.Optional[builtins.str] = None,
    hostname: typing.Optional[typing.Union[ListItemsHostname, typing.Dict[builtins.str, typing.Any]]] = None,
    ip: typing.Optional[builtins.str] = None,
    redirect: typing.Optional[typing.Union[ListItemsRedirect, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afafc25338fa4fc5dfa9651b49c07d8387bb3f8e92bd26e4aac202e24c241d82(
    *,
    url_hostname: builtins.str,
    exclude_exact_hostname: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28cb1b8350060e8eb1cf85fd0edde6f3d2c24eaaadb345e8197404a11a07ff5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5aaaff16c5ce7565fb86c08312a20f32d4db25effb9080df9e7b6eaa567255(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a9b00d781ee45194c74f4809f647ddfdf09883bcc513df2b20fa7b501a759c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6db1cbe379d591886422fe74f784f8b2f877cca4a19b12ae5790ddda51a1b3c4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsHostname]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4393aec9d8f32ba54654bb293ec44573cdb56b6de19515b1fed1fe6d554490a2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c34da65a0cb78f1d93d85c2630005d33aff90698c02e30993cfa016b4912ee5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d47889e1f47249196e64b61653ab060be7023a7538a7525d3ad8989534858d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74198b6987edfe61370523dbf9fc7d24690dede2ee400a2c68bdf78846134aa1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__836161a62137689b919b86c8271bff6e587a322ecc9aacd25d8a83829ce8773b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026778b836b369015d734472b222c6766c72d7fc3ee1cbf148bd9d8bac47d17b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ListItems]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e9496a66d5911b8a5d93bdb5757d190fd01c94974ac39b3e0cd4df9efc98bde(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34f1d5032b26e590551c2157185b2ed0e829cb4cdde56ee4529f2d7c779e0730(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a23dc73c9ed3e8eef21a4704c12c85c24a2cf729d3a76acea0ec3498d2b2e506(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47baf98e78840c1b4f90b473eb9e8ce271872f5df3b3c09b7102fd05adedcdab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__158c512e5253432e864c9e4b1ff7b30dd2e0ff26993d9ba311f222b0d056ecdd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItems]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__121f2d5476076731519fe0692528af2981d6bc3fd4fca79e6908deb5d399b2e8(
    *,
    source_url: builtins.str,
    target_url: builtins.str,
    include_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    preserve_path_suffix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    preserve_query_string: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    status_code: typing.Optional[jsii.Number] = None,
    subpath_matching: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1ce9538d6bf6e87f7d7e0a3f88fec42feee2ba5e3c03f65d4999cd59c4c29de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d705a4132aaf194d3c045f5a8a38e3d822270a18846e47ca66e8eb8e45615d98(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2779dca5b97f1b4b970e35d08f1068a48217be7dad33c3ba79e6ac5c1b2b59a1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e237f409159c5b9512a0f967dcf597a776ea91f07f681e92db05bf306ee69d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd2364eb064e5efa326a6d3907184f820843b98f757b26e98fff7adbe441c561(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40aefa532f6346fc75f66d1fb505262351acf6c8f36242dd698e126a208f639e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__793e15f00cc69ec9ef181a1c7a5dd3a7b2e76dd9f5c1c13a3d39fea9f2aa6c04(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60c15af6cbe3b9bc510222228c7d47f9458d76e41578549b8d833ee40aec80fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef6d034026ab2ac1895db9258f7fe0d0b8f483d519ba0bc62406e9da6e17079a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ListItemsRedirect]],
) -> None:
    """Type checking stubs"""
    pass
