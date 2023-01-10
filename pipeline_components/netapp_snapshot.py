def create_snapshot(
  namespace: str, 
  pvc_name: str,
  snapshot_name:str, 
  volume_snapshot_class :str="csi-snapclass",
  ) -> str:
  import netapp_dataops.k8s as ndt

  # Take snapshot
  print(f"Namespacce: {namespace}")
  print(f"PVC name: {pvc_name}")
  print(f"Snapshot name: {snapshot_name}")
  print(f"VolumeSnapshotClass name: {volume_snapshot_class}")

  ndt.create_volume_snapshot(
    pvc_name=pvc_name, 
    snapshot_name=snapshot_name, 
    volume_snapshot_class=volume_snapshot_class, 
    namespace=namespace)
    
  print("Taking snapshot has be successfully completed")

  return snapshot_name