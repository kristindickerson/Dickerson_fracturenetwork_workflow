import bpy
import random


# Total dimensions of the box (10 m x 10 m x 10 m)
box_length = 10  # 10 meters
box_width = 10  # 10 meters

# Fractures
num_fractures=50
fracture_size=(0.1, 0.05)


# Function to create a box with a transparent material
def create_layer(location, dimensions, color, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cube = bpy.context.object
    cube.name = name
    cube.scale = (dimensions[0] / 2, dimensions[1] / 2, dimensions[2] / 2)
    
    mat = bpy.data.materials.new(name=f"{name}_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Alpha"].default_value = 0.3
    mat.blend_method = 'BLEND'
    mat.shadow_method = 'NONE'
    
    cube.data.materials.append(mat)
    
    return cube  # Return the created layer for later reference

# Function to create a rectangular plane (instead of ellipse)
def create_rectangular_plane(location, width, height, name):
    # Create a plane (rectangular shape by scaling the plane)
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    plane = bpy.context.object
    plane.name = name
    
    # Debug print to ensure location is correct
    print(f"Creating plane at location: {location}")
    
    # Scale the plane to the desired dimensions (width x height)
    plane.scale = (width / 2, height / 2, 1)  # Scaling the plane to make it rectangular
    
    # Set a material to make the plane visible and colored
    mat = bpy.data.materials.new(name="PlaneMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0, 0, 1, 1)  # Blue color for visibility
    plane.data.materials.append(mat)
    
    return plane

# Function to create random fractures (elliptical planes) in the middle layer
def create_random_fractures(layer_object, num_fractures, fracture_size):  # Minor and Major axes for the ellipse
    # Get the dimensions of the middle layer
    layer_dimensions = layer_object.scale
    layer_width = layer_dimensions[0] * 2  # Width = X axis * 2
    layer_depth = layer_dimensions[1] * 2  # Depth = Y axis * 2
    layer_height = layer_dimensions[2] * 2  # Height = Z axis * 2
    
    # Middle layer's Z bounds (since the middle layer is centered at the origin)
    z_min = -layer_height / 2 -3.2
    z_max = layer_height / 2 - 4.7
    
    for i in range(num_fractures):
        # Randomly choose the position for each fracture within the blue layer's bounds
        fracture_location = (
            random.uniform(-5/2, 5/2),
            random.uniform(-5/2, 5/2),
            random.uniform(z_min, z_max)  # Ensure fractures are within the blue layer's height
        )
        
        # Create an ellipse plane (a stretched circle) to simulate a fracture
        bpy.ops.mesh.primitive_circle_add(radius=1, location=fracture_location, fill_type='NGON')
        fracture = bpy.context.object
        fracture.name = f"Fracture_{i}"
        
        # Scale the circle to make it elliptical
        fracture.scale = (random.uniform(fracture_size[0], fracture_size[0] * 2),  # Major axis (X)
                          random.uniform(fracture_size[1], fracture_size[1] * 2),  # Minor axis (Y)
                          0.01)  # Small Z scale to keep it flat

        # Random rotation for added realism
        fracture.rotation_euler = (
            random.uniform(0, 3.14),
            random.uniform(0, 3.14),
            random.uniform(0, 3.14)
        )
        
        # Create a random color for each fracture for better visualization
        mat = bpy.data.materials.new(name=f"Fracture_{i}_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (
            random.uniform(0.5, 1), random.uniform(0, 0.5), random.uniform(0, 0.5), 1
        )  # Random color
        bsdf.inputs["Alpha"].default_value = 1  # Fracture is fully opaque
        mat.blend_method = 'BLEND'
        fracture.data.materials.append(mat)

# Parameters for the layers
layers = [
    {"name": "TopLayer", "height": 1, "color": (1, 1, 0, 1)},  # Yellow
    {"name": "MiddleLayer", "height": 3, "color": (0, 0, 1, 1)},  # Blue
    {"name": "BottomLayer", "height": 6, "color": (1, 0, 0, 1)}  # Red
]

# Calculate the total height of all layers
total_height = sum(layer["height"] for layer in layers)

# Calculate the starting Z position to center the entire stack around the origin
current_bottom = -total_height / 2  # This will place the center of the stack at Z = 0

# Create the layers stacked together
middle_layer_object = None
for layer in layers:
    height = layer["height"]  # Height in meters
    
    if layer["name"] == "BottomLayer":
        location = (0, 0, current_bottom - 0.75)  # Adjust the BottomLayer location
    else:
        location = (0, 0, current_bottom)  # For other layers, just use current_bottom
    
    create_layer(
        location=location,  # Stack each layer on top
        dimensions=(box_length, box_width, height),
        color=layer["color"],
        name=layer["name"]
    )
    
    if layer["name"] == "MiddleLayer":
        middle_layer_object = bpy.context.object  # Store the reference to the middle layer
        
    if layer["name"] == "TopLayer":
        top_layer_object = bpy.context.object  # Store the reference to the middle layer
    
    current_bottom += height  # Move the bottom position up for the next layer

# Add random fractures to the middle (blue) layer
if middle_layer_object:
    create_random_fractures(middle_layer_object, num_fractures, fracture_size)  # Add 50 fractures

# Create two separate rectangular planes at the same height (overlapping blue and yellow layers)
# Plane 1: At the edge of the blue layer (MiddleLayer), 0.2 meters from the center
# Plane 2: 0.2 meters spaced from the first, at the edge of the yellow layer (TopLayer)

if middle_layer_object and top_layer_object:
    # Calculate the height of the planes based on the layers' positions
    middle_layer_z = middle_layer_object.location.z  # Z location of the middle (blue) layer
    top_layer_z = top_layer_object.location.z  # Z location of the top (yellow) layer

    # The planes should be positioned at the midpoint of these layers' heights
    planes_z = (middle_layer_z + top_layer_z) / 2

    # Plane 1: At the edge of the blue layer
    plane1_location = (box_length / 2 + 0.1, 0, planes_z)  # Offset 0.1 from the center of the box
    create_rectangular_plane(location=plane1_location, width=0.4, height=0.75, name="RectangularPlane1")
    
    # Plane 2: Spaced 0.2 meters from Plane 1 along the x-axis
    plane2_location = (box_length / 2 + 0.3, 0, planes_z)  # Offset 0.3 from the center of the box
    create_rectangular_plane(location=plane2_location, width=0.4, height=0.75, name="RectangularPlane2")