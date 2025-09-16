#import font
#import camera

@group(0) @binding(30) var<storage> u_text : Texts;

struct Texts {
  n_texts: u32,
  data: array<u32>, // check in python code of label.py on how the data is stored
};

struct TextData {
  pos: vec3f,
  shift: vec2f,
  length: u32,
  ichar: u32,
  char: u32,
  apply_camera: u32,
};

fn textLoadData(i: u32) -> TextData {
    let offset = u_text.n_texts * 4 + i * 2;
    let itext = u_text.data[ offset ];
    let char_data = u_text.data[ offset + 1 ];
    let ichar = extractBits(char_data, 0u, 16u);
    let char = extractBits(char_data, 16u, 16u);

    let offset_text = itext * 4;
    let pos = vec3f(bitcast<f32>(u_text.data[offset_text]), bitcast<f32>(u_text.data[offset_text + 1]), bitcast<f32>(u_text.data[offset_text + 2]));
    let text_data = u_text.data[offset_text + 3];
    let length = extractBits(text_data, 0u, 16u);
    let apply_camera = extractBits(text_data, 16u, 8u);

    let x_align = f32(extractBits(text_data, 24u, 2u));
    let y_align = f32(extractBits(text_data, 26u, 2u));

    let shift = vec2<f32>(-0.5 * x_align - 0.278/f32(length), -0.5 * y_align - 0.20);

  return TextData(pos, shift, length, ichar, char, apply_camera);
}

@vertex
fn vertexText(@builtin(vertex_index) vertexId: u32, @builtin(instance_index) charId: u32) -> FontFragmentInput {
    let text = textLoadData(charId);

    var position = vec4f(text.pos, 1.0);
    if (text.apply_camera != 0) {
        position = cameraMapPoint(text.pos);
    }

    let char_size = fontGetSizeOnScreen();

    position.x += f32(text.ichar) * char_size.z * position.w;

    let shift = text.shift;
    position.x += char_size.x * shift.x * f32(text.length) * position.w;
    position.y += char_size.y * shift.y * position.w;

    // snap position to pixel grid
    let resolution = vec2f(f32(u_camera.width), f32(u_camera.height));
    let ndc = position.xy / position.w;
    let screen = (ndc * 0.5 + vec2f(0.5)) * resolution;
    let snapped_screen = floor(screen) + 0.5;
    let snapped_ndc = (snapped_screen / resolution - vec2f(0.5)) * 2.0;
    position.x = snapped_ndc.x * position.w;
    position.y = snapped_ndc.y * position.w;

    return fontCalc(text.char, position, vertexId);
}
