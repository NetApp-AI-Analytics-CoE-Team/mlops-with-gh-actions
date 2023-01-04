def create_snapshot(
  namespace: str, 
  pvc_name: str,
  snapshot_name:str, 
  volume_snapshot_class :str="csi-snapclass",
  ) -> str:
  import netapp_dataops.k8s as ndt
  # import datetime

  # Generate snapshot name with timestamp
  # timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y%m%d%H%M%S')
  # snapshot_name = pvc_name + "-" + timestamp

  # Take snapshot
  try: 
    ndt.create_volume_snapshot(
      pvc_name=pvc_name, 
      snapshot_name=snapshot_name, 
      volume_snapshot_class=volume_snapshot_class, 
      namespace=namespace)

    # output = {
    #   "pvc_name": pvc_name, 
    #   "snapshot_name": snapshot_name, 
    #   "volume_snapshot_class": volume_snapshot_class, 
    #   "namespace": namespace,
    #   "message": "Taking snapshot has be successfully completed"
    # }
    print("Taking snapshot has be successfully completed")
  # Error handling
  except InvalidConfigError:
    # output = {
    #     "message": "Failed taking snapshot because of invalid kubeconfig"
    # }
    print("Failed taking snapshot because of invalid kubeconfig")
  except APIConnectionError:
    # output = {
    #     "message": "Failed taking snapshot because of connection to the Kubernetes API"
    # }
    print("Failed taking snapshot because of connection to the Kubernetes API")

  return snapshot_name