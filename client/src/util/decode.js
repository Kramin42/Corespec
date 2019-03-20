function decode_data(data) {
  var blob = atob(data.base64)
  var buffer = new ArrayBuffer(blob.length)
  var dView = new DataView(buffer)
  for (var i=0; i<blob.length; i++) {
    dView.setUint8(i, blob.charCodeAt(i))
  }
  if (data.dtype === "float64") {
    return new Float64Array(buffer)
  } else if (data.dtype === "float32") {
    return new Float32Array(buffer)
  } else {
    console.log('unknown base64 format '+data.dtype);
  }
}

function decode_plot_data(data) {
  for (let i=0; i<data.length; i++) {
    data[i].x = decode_data(data[i].x)
    data[i].y = decode_data(data[i].y)
    if (data[i].z) data[i].z = decode_data(data[i].z)
  }
  return data
}

export {decode_plot_data, decode_data};
