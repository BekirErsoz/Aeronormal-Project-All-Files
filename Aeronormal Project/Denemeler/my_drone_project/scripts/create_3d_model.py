import open3d as o3d

def create_3d_model(point_cloud_file):
    pcd = o3d.io.read_point_cloud(point_cloud_file)
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, alpha=0.02)
    mesh.compute_vertex_normals()
    o3d.io.write_triangle_mesh("3d_model.ply", mesh)
    return mesh

mesh = create_3d_model("pointcloud.pcd")
o3d.visualization.draw_geometries([mesh])