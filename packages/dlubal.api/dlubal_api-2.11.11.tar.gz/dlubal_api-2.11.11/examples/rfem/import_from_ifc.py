import os
from dlubal.api import rfem
from dlubal.api import common

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    rfem_app.create_model(name='ifc_structure')

    # Import IFC model
    example = os.path.join(os.path.dirname(__file__), 'src', 'ifc_structure.ifc')

    rfem_app.import_from(
        filepath=example,
        import_attributes=common.import_export.IfcImportAttributes()
    )

    # Get all imported IFC models
    ifc_models = rfem_app.get_object_list([rfem.ifc_objects.IfcFileModelObject()])

    # Edit IFC model
    ifc_model = ifc_models[0]
    edited_ifc_model = rfem.ifc_objects.IfcFileModelObject(
        no=ifc_model.no,
        mirror_axis_z=True)
    rfem_app.update_object(edited_ifc_model)


    # Get all IFC objects
    ifc_model_objects = rfem_app.get_object_list([rfem.ifc_objects.IfcModelObject()])

    members = list()
    surfaces = list()
    solids = list()

    # Find IFC objects that will be converted to straight members and solids
    for ifc_object in ifc_model_objects:
        ifc_type = ifc_object.ifc_type
        if ifc_type in ["IfcColumn", "IfcBeam"]:
            members.append(ifc_object)
        elif ifc_type in ["IfcWallStandardCase", "IfcSlab",]:
            surfaces.append(ifc_object)
        elif ifc_type in ["IfcFooting"]:
            solids.append(ifc_object)

    rfem_app.convert_objects(
        convert_into=common.ConvertObjectInto.CONVERT_IFC_OBJECT_INTO_STRAIGHT_MEMBER,
        objects=members
    )

    rfem_app.convert_objects(
        convert_into=common.ConvertObjectInto.CONVERT_IFC_OBJECT_INTO_SURFACE,
        objects=surfaces
    )

    rfem_app.convert_objects(
        convert_into=common.ConvertObjectInto.CONVERT_IFC_OBJECT_INTO_SOLID,
        objects=solids
    )

    # rfem_app.delete_object_list(ifc_models)
