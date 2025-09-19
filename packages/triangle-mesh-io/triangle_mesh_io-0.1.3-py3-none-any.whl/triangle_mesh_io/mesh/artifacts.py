import numpy as np
import copy


def remove_artifacts_from_vertices_and_faces(vertices, faces):
    faces = remove_faces_with_less_than_three_unique_vertices(faces=faces)
    vertices, faces = remove_vertices_which_are_not_used_by_faces(
        vertices=vertices, faces=faces
    )
    return vertices, faces


def remove_faces_with_less_than_three_unique_vertices(faces):
    """
    Removes faces which only have two or one unique vertices and thus do not
    have a surface in 3D-space.
    """
    out_faces = []

    for face_idx in range(faces.shape[0]):
        face = faces[face_idx]
        num_uniqie_vertices = len(set(face))
        if num_uniqie_vertices == 3:
            out_faces.append(face)
    return np.asarray(out_faces, dtype=int)


def remove_vertices_which_are_not_used_by_faces(vertices, faces):
    out_vertices = []
    out_faces = []
    vertex_use = {}

    for face_idx in range(faces.shape[0]):
        face = faces[face_idx]
        new_face = []
        for vertex_idx in face:
            if vertex_idx not in vertex_use:
                vertex_use[vertex_idx] = len(vertex_use)
                out_vertices.append(vertices[vertex_idx])
            new_face.append(vertex_use[vertex_idx])
        out_faces.append(new_face)
    return np.asarray(out_vertices, dtype=float), np.asarray(
        out_faces, dtype=int
    )


def remove_vertex_normals_which_are_not_used_by_faces(obj):
    out = {"v": copy.copy(obj["v"]), "vn": [], "mtl": {}}
    vn_use = {}

    for mtl in obj["mtl"]:
        out["mtl"][mtl] = []
        for face_idx in range(len(obj["mtl"][mtl])):
            old_face = obj["mtl"][mtl][face_idx]
            new_face = {"v": old_face["v"], "vn": []}

            for vn in old_face["vn"]:
                if vn not in vn_use:
                    vn_use[vn] = len(vn_use)
                    out["vn"].append(obj["vn"][vn])
                new_face["vn"].append(vn_use[vn])
            out["mtl"][mtl].append(new_face)

    return out
