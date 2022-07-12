from ursina import *
from ursina import Shader

oblivion_postprocessing = Shader(
    fragment='''
#version 430

// SETUP VARIABLES ======
uniform sampler2D tex;
in vec2 window_size;
in vec2 uv;

// for pixelation
uniform bool pixelated;
uniform float pixel_size;

// for blur start
uniform float blur_size;
uniform bool horizontal;
// for blur end

// grayscale start
uniform float alpha;
// grayscale end

out vec4 color;
out vec4 color_gray;

// ===========================

void main() {
    // for pixelation
    float Pixels = pixel_size;
    float dx = 9.0 * (1.0 / Pixels);
    float dy = 16.0 * (1.0 / Pixels);
    vec2 new_uv = vec2(dx * floor(uv.x / dx), dy * floor(uv.y / dy));

    // for blur
    color = texture(tex, uv).rgba;
    vec4 col_vblur = vec4(0.);
    
    // for grayscale
    vec4 rgb = texture(tex, uv).rgba;
    float gray = rgb.r*.3 + rgb.g*.59 + rgb.b*.11;
    

    // for blur
    for(float index=0; index<10; index++) {
        // add color at position (Vertical or Horizontal) to color
        if (horizontal){
            vec2 offset_uv_vblur = uv + vec2((index/9 - 0.5) * blur_size, 0);
            col_vblur += texture(tex, offset_uv_vblur);
        }else{
            vec2 offset_uv_vblur = uv + vec2(0, (index/9 - 0.5) * blur_size);
            col_vblur += texture(tex, offset_uv_vblur);
        }
    }

    // for blur
    col_vblur = col_vblur / 10;
    col_vblur = 1-((1-color)*(1-col_vblur));
    
    // for grayscale
    color_gray = vec4(gray, gray, gray, 1.0);
    
    // mixing
    color = mix(mix(color ,color_gray,alpha), vec4(col_vblur.rgb, 1), blur_size*10);
    if (pixelated){
    color = mix(color, texture(tex, new_uv),1);
    }
    
// ===================================
}
''',
    default_input=dict(
        pixelated=False,
        pixel_size=1500,
        alpha=1.0,
        blur_size=.1,
        horizontal=False
    ))
