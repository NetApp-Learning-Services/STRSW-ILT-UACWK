# App Classes

These classes are all related to `apps`, and all inherit the [SDKCommon](../baseClasses/README.md#SDKCommon) class.

## getApps

| **Endpoint** | `/accounts/{account_id}/topology/v1/apps` |
| **Method** | `GET` |
| **Data** | `{}` |
| **Params** | `{}` |

`getApps` makes an API call to gather **all** apps known to Astra, and then removes unneeded apps/data from the reponse object depending upon various filters:

* `discovered`: whether to show discovered (i.e. non-managed) apps (default `False`)
* `source`: filter by the app source, for example "helm" or "namespace" (default `None`)
* `namespace`: filter by the namespace the app is in (default `None`)
* `cluster`: filter by a specific Kubernetes cluster (default `None`)
* `ignored`: whether to show ignored apps (default `False`)
* `delPods`: whether or not to delete the `pods` key/value of the `dict` response to minimize the output (default `True`)

Init?
