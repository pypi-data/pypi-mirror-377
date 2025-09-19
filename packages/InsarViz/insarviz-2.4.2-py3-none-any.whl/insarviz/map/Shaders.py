#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# constants #################################################################

DATA_UNIT, COLORMAP_UNIT = range(2)  # texture unit use


# common shaders ############################################################

VERT_SHADER = r"""
    #version 330

    uniform mat4 model_matrix;
    uniform mat4 view_matrix;
    uniform mat4 projection_matrix;

    layout (location = 0) in vec3 vertex;
    layout (location = 1) in vec2 tex_coord;

    out vec2 tex_coord0;

    void main() {
        gl_Position = projection_matrix * view_matrix * model_matrix * vec4(vertex, 1.);
        tex_coord0 =  tex_coord;
    }
"""

ALPHA_SHADER = r"""
    #version 330

    uniform float alpha;

    vec4 apply_alpha(vec4 color) {
        return vec4(color.rgb, color.a*alpha);
    }
"""

COLORMAP_SHADER = r"""
    #version 330

    uniform sampler2D values;
    uniform sampler1D colormap;

    uniform float v0; // lower and
    uniform float v1; // upper bound of data values mapped to the colormap

    uniform float cutoff; // cutoff, to hide part of the layer

    vec4 apply_alpha(vec4 color);

    in vec2 tex_coord0;
    out vec4 frag_color;

    void main() {
        // get values (x) and mask (y)
        if(tex_coord0.x < cutoff) { discard; }
        vec4 t = texture(values, tex_coord0);
        vec2 v = t.xy;
        // if mask < 0.5 then more than half of values represented by pixel are nodata
        if(v.y < 0.5) { discard; }
        // get the color in the colormap 
        // "v.x/v.y" because v.y is the proportion of values that are not nodata
        vec4 l = texture(colormap, ((v.x/v.y)-v0)/(v1-v0));
        frag_color = apply_alpha(vec4(l.rgb, 1.));
    }
"""

IMAGE_RGB_SHADER = r"""
    #version 330

    vec4 apply_alpha(vec4 color);

    uniform sampler2D image;

    uniform float cutoff; // cutoff, to hide part of the layer

    in vec2 tex_coord0;
    out vec4 frag_color;

    void main() {
        if(tex_coord0.x < cutoff) { discard; }
        frag_color = apply_alpha(texture(image, tex_coord0));
    }
"""

# MiniMapView shaders for MapView viewport rect ####################################################

VIEWPORTRECT_VERT_SHADER = r"""
    #version 330

    uniform mat4 model_matrix;
    uniform mat4 view_matrix;
    uniform mat4 projection_matrix;

    layout (location = 0) in vec3 vertex;

    void main() {
        gl_Position = projection_matrix * view_matrix * model_matrix * vec4(vertex, 1.);
    }
"""

VIEWPORTRECT_FRAG_SHADER = r"""
    #version 330

    uniform vec4 rect_color;

    out vec4 frag_color;

    void main() {
        frag_color = rect_color;
    }
"""
