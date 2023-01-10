# How to create static users in Kubeflow
## Prerequisite
- installed Kubeflow in multi user mode(see: https://www.kubeflow.org/docs/components/multi-tenancy/getting-started/)

## Considerations
- if your user accounts have no permissions to any exisiting profiles, a profile named as your username is automatically created when you log-in Kubeflow UI first time.

## Procedure
1. export configmap dex using
```
kubectl get configmap dex -n auth -o jsonpath='{.data.config\.yaml}' > dex-yaml.yaml
```

2. edit exported configmap
```diff
issuer: http://dex.auth.svc.cluster.local:5556/dex
storage:
  type: kubernetes
  config:
    inCluster: true
web:
  http: 0.0.0.0:5556
logger:
  level: "debug"
  format: text
oauth2:
  skipApprovalScreen: true
enablePasswordDB: true
staticPasswords:
 - email: user@example.com
  hash: $2y$12$4K/VkmDd1q1Orb3xAt82zu8gk7Ad6ReFR4LCP9UeYE90NLiN9Df72
  # https://github.com/dexidp/dex/pull/1601/commits
  # FIXME: Use hashFromEnv instead
  username: user
  userID: "15841185641784"
+ - email: yshimizu@netapp.com
+   hash: $2a$12$tvOJwWyoMkyCcT4WG.LM.eCzFEIMxGjcYA.rECRueHDSH8utHJ8l2
+   # note: your password should be Bcrypt hased 
+   # Bcrypt hash generator: https://bcrypt-generator.com/
+   username: yshimizu
staticClients:
# https://github.com/dexidp/dex/pull/1664
 - idEnv: OIDC_CLIENT_ID
  redirectURIs: ["/login/oidc"]
  name: 'Dex Login Application'
  secretEnv: OIDC_CLIENT_SECRET
```

3. replace original configmap
```
kubectl create configmap dex --from-file=config.yaml=dex-yaml.yaml -n auth --dry-run=client -o yaml | kubectl apply -f -
```

4. update the dex deployment
```
kubectl rollout restart deployment dex -n auth
```

5. verify that dex pod updated
```
kubectl get pod -n auth
```