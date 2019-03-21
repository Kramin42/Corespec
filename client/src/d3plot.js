// Cameron Dykstra
// dykstra.cameron@gmail.com

import * as d3 from 'd3';
import {xyzoom, xyzoomTransform, xyzoomIdentity} from 'd3-xyzoom';
d3.xyzoom = xyzoom;
d3.xyzoomTransform = xyzoomTransform;
d3.xyzoomIdentity = xyzoomIdentity;

function zip(arrays) {
  return arrays[0].map(function(_,i){
      return arrays.map(function(array){return array[i]})
  });
}

function xyzip(xs, ys) {
  var zipped = []
  for (var i=0; i<xs.length; i++) {
    zipped[i] = {x: xs[i], y: ys[i]}
  }
  return zipped
}

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  )
}

export function d3plot_contour(svg, plotDef) {
  var MAX_DISPLAY_POINTS = 1000
  var width = 600
  var height = 400
  var margin = {left: 60, right: 20, top: 30, bottom: 40}
  var f_w = 60
  var f_h = 13
  var fontS = 12
  var fontM = 14
  var fontL = 16
  var w = width-margin.left-margin.right
  var h = height-margin.top-margin.bottom
  svg.selectAll('*').remove()
  svg.attr('viewBox', '0 0 '+width+' '+height)

  var x = plotDef.data[0].x
  var y = plotDef.data[0].y
  var z = plotDef.data[0].z

  // transform = ({type, value, coordinates}) => {
  //   return {type, value, coordinates: coordinates.map(rings => {
  //     return rings.map(points => {
  //       return points.map(([x, y]) => ([
  //         grid.x + grid.k * x,
  //         grid.y + grid.k * y
  //       ]))
  //     })
  //   })}
  // }

  var contours = d3.contours().size([x.length, y.length])(z)
  console.log(contours)
  var color = d3.scaleLinear().domain(d3.extent(z)).interpolate(d => d3.interpolateRgb('#ffffff', '#000000'))

  var base_scale_x = d3.scaleLinear()
    .domain([d3.min(x),d3.max(x)])
    .range([0,w]);
  var base_scale_y = d3.scaleLinear()
    .domain([d3.min(y),d3.max(y)])
    .range([h,0]);
  var scale_x = base_scale_x.copy()
  var scale_y = base_scale_y.copy()

  var path = d3.geoPath().projection(
    d3.geoTransform({
      point: (x, y) => this.stream.point(scale_x(x), scale_y(y))
    })
  )

  var g = svg.append('g')
    .attr('transform', 'translate('+margin.left+','+margin.top+')')

  for (const contour of contours) {
    g.append('path')
      .attr('d', path(contour))
      .attr('fill', color(contour.value))
  }
  // g.append('g')
  //     .attr('fill', 'none')
  //     .attr('stroke', '#fff')
  //     .attr('stroke-opacity', 0.5)
  //   .selectAll('path')
  //   .data(contours)
  //   .join('path')
  //     .attr('fill', d => colour(d.value))
  //     .attr('d', d3.geoPath())
}

export function d3plot(svg, plotDef) {
  var MAX_DISPLAY_POINTS = 1000
  var width = 600
  var height = 400
  var margin = {left: 60, right: 20, top: 30, bottom: 40}
  var f_w = 60
  var f_h = 13
  var fontS = 12
  var fontM = 14
  var fontL = 16
  var w = width-margin.left-margin.right
  var h = height-margin.top-margin.bottom
  svg.selectAll('*').remove()
  svg.attr('viewBox', '0 0 '+width+' '+height)
  var plotColors = ['#0072bd', '#d95319', '#edb120', '#7e2f8e', '#77ac30','#4dbeee','#a2142f']
  var numPlotColors = 7

  var data = []
  var dataLabels = []
  var domain = {}
  plotDef.data.forEach(d => {
    if (domain.left) domain.left = Math.min(domain.left, d3.min(d.x))
    else domain.left = d3.min(d.x)
    if (domain.right) domain.right = Math.max(domain.right, d3.max(d.x))
    else domain.right = d3.max(d.x)
    if (domain.bot) domain.bot = Math.min(domain.bot, d3.min(d.y))
    else domain.bot = d3.min(d.y)
    if (domain.top) domain.top = Math.max(domain.top, d3.max(d.y))
    else domain.top = d3.max(d.y)
    data.push(xyzip(d.x, d.y))
    dataLabels.push(d.name)
  })

  var SITickFormatX = d3.format('.4~s')
  var SITickFormatY = d3.format('.3~s')
  var SIFocusFormat = d3.format('.5~s')
  var tickFormatX = (val) => {return SITickFormatX(val).replace(/µ/,'\u03bc')}
  var tickFormatY = (val) => {return SITickFormatY(val).replace(/µ/,'\u03bc')}
  var focusFormat = (val) => {return SIFocusFormat(val).replace(/µ/,'\u03bc')}

  var base_scale_x = d3.scaleLinear()
    .domain([domain.left,domain.right])
    .range([0,w]);
  var base_scale_y = d3.scaleLinear()
    .domain([domain.bot,domain.top])
    .range([h,0]);
  var scale_x = base_scale_x.copy()
  var scale_y = base_scale_y.copy()
  var axis_x = d3.axisBottom()
    .scale(scale_x)
    .ticks(10)
    .tickFormat(tickFormatX)
  var axis_y = d3.axisLeft()
    .scale(scale_y)
    .ticks(10)
    .tickFormat(tickFormatY)
  var bisect_x = d3.bisector(d => {return d.x}).left
  var zoom = d3.xyzoom()
    .extent([[0, 0], [w, h]])
    .scaleExtent([[1, Infinity],[1, Infinity]])
    .translateExtent([[0, 0], [w, h]])
    .on('zoom', zoomed)
  var zoom_x = d3.xyzoom()
    .extent([[0, 0], [w, h]])
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [w, h]])
    .on('zoom', zoomed_x)
  var zoom_y = d3.xyzoom()
    .extent([[0, 0], [w, h]])
    .scaleExtent([1, Infinity])
    .translateExtent([[0, 0], [w, h]])
    .on('zoom', zoomed_y)
  var line = d3.line()
    .x(d => scale_x(d.x))
    .y(d => scale_y(d.y))
  var g = svg.append('g')
    .attr('transform', 'translate('+margin.left+','+margin.top+')')
    .append('g')

  //title
  if (plotDef.layout.title) {
    svg.append('text')
      .attr('class', 'title')
      .attr('font-size', fontL)
      .attr('fill', '#333')
      .attr('x', width/2)
      .attr('y', margin.top/2 + fontL/2)
      .style('text-anchor', 'middle')
      .text(plotDef.layout.title)
  }

  //white fill and border
  g.append('rect')
    .attr('width', w)
    .attr('height', h)
    .attr('fill', 'white')
    .attr('stroke', 'black')

  // plot area clip
  var clipID = uuidv4()
  g.append('clipPath')
    .attr('id', clipID)
    .append('rect')
    .attr('width', w)
    .attr('height', h)

  // axes
  var axis_x_g = g.append('g')
    .attr("class", "x axis")
    .attr("transform", "translate(-0.5," + (h-0.5) + ")")
    .call(axis_x)
  if (plotDef.layout.xaxis) {
    axis_x_g.append('text')
      .attr('font-size', fontM)
      .attr('dx', w/2)
      .attr('dy', margin.bottom-fontM/4)
      .style('text-anchor', 'middle')
      .text(plotDef.layout.xaxis.title)
  }
  var axis_y_g = g.append('g')
    .attr("class", "y axis")
    .attr("transform", "translate(-0.5," + (-0.5) + ")")
    .call(axis_y)
  if (plotDef.layout.yaxis) {
  axis_y_g.append('text')
    .attr('font-size', fontM)
    .attr('transform', 'rotate(-90)')
    .attr('dx', -h/2)
    .attr('dy', -margin.left+fontM)
    .style('text-anchor', 'middle')
    .text(plotDef.layout.yaxis.title)
  }

  // plot data lines
  var plotPaths = []
  for (var i=0; i<data.length; i++) {
    var path = g.append('path')
      .datum(data[i])
      .attr("class", "line")
      .attr('d', line)
      .attr('clip-path', 'url(#'+clipID+')')
      .attr('fill', 'none')
      .attr('stroke', plotColors[i%numPlotColors])
      .attr('stroke-width', 1.5)
      .attr('stroke-miterlimit', 2)
      .attr('vector-effect', 'non-scaling-stroke')
    plotPaths.push(path)
  }
  update()

  //legends
  var legends = []
  for (var i=0; i<data.length; i++) {
    if (dataLabels[i]) {
      var offsetY = fontS/2 + i*1.5*fontS
      var offsetX = -fontS/2
      var legend = g.append('g')
        .attr('class', 'legend')
      var txt = legend.append('text')
        .text(dataLabels[i])
        .attr('font-size', fontS)
        .attr('dy', '0.85em')
      var txtlen = txt.node().getComputedTextLength()
      txt.attr('x', w+offsetX-txtlen).attr('y', offsetY)
      legend.append('rect')
        .attr('x', w+offsetX-fontS/4-txtlen-fontS).attr('y', offsetY)
        .attr('width', fontS).attr('height', fontS)
        .attr('fill', plotColors[i%numPlotColors])
      legends.push(legend)
    }
  }

  // crosshairs
  var crosshairX = g.append('line')
    .attr('class', 'focus')
    .style('display', 'none')
    .attr('y1', 0)
    .attr('y2', h)
    .attr('stroke', '#333')
    .attr('clip-path', 'url(#'+clipID+')')
  var crosshairs = []
  for (var i=0; i<data.length; i++) {
    var crosshair = g.append('line')
      .attr('class', 'focus')
      .style('display', 'none')
      .attr('x1', 0)
      .attr('x2', w)
      .attr('stroke', plotColors[i%numPlotColors])
      .attr('clip-path', 'url(#'+clipID+')')
    crosshairs.push(crosshair)
  }

  //focus labels
  var focusX = g.append('g')
    .attr('class', 'focus')
    .style('display', 'none')
  focusX.append('rect')
    .attr('width', f_w)
    .attr('height', f_h)
    .style('fill', '#333')
  focusX.append('text')
    .attr('font-size', fontS)
    .attr('dx', '0.25em')
    .attr('dy', '0.85em')
  var lineFoci = []
  for (var i=0; i<data.length; i++) {
    var focus = g.append('g')
      .attr('class', 'focus')
      .style('display', 'none')
    focus.append('circle')
      .attr('r', 1)
      .attr('clip-path', 'url(#'+clipID+')')
    focus.append('rect')
      .attr('width', f_w)
      .attr('height', f_h)
      .style('fill', plotColors[i%numPlotColors])
      .attr('clip-path', 'url(#'+clipID+')')
    focus.append('text')
      .attr('font-size', fontS)
      .attr('dx', '0.25em')
      .attr('dy', '0.85em')
      .attr('clip-path', 'url(#'+clipID+')')
    lineFoci.push(focus)
  }

  var overlay = g.append('rect')
    .attr('class', 'zoom-xy overlay')
    .attr('width', w)
    .attr('height', h)
    .call(zoom)
    .on('mouseout', () => {g.selectAll('.focus').style('display', 'none')})
    .on('mousemove', update_hover)

  g.append('rect')
    .attr('class', 'zoom-x overlay')
    .attr('width', w)
    .attr('height', margin.bottom)
    .attr('transform', 'translate('+0+','+h+')')
    .call(zoom_x)
    .on('mouseout', () => {g.selectAll('.focus').style('display', 'none')})
    .on('mousemove', update_hover)

  g.append('rect')
    .attr('class', 'zoom-y overlay')
    .attr('width', margin.left)
    .attr('height', h)
    .attr('transform', 'translate('+(-margin.left)+','+0+')')
    .call(zoom_y)

  function zoomed() {
    g.select('rect.zoom-x').call(zoom_x.transform, d3.event.transform)
    g.select('rect.zoom-y').call(zoom_y.transform, d3.event.transform)
  }

  function zoomed_x() {
    var e_t = d3.event.transform
    var xy_t = d3.xyzoomTransform(g.select('rect.zoom-xy').node())
    var new_t = d3.xyzoomIdentity.translate(e_t.x,xy_t.y).scale(e_t.kx,xy_t.ky)
    g.select('rect.zoom-xy').property('__zoom', new_t)
    scale_x = d3.event.transform.rescaleX(base_scale_x)
    svg.select(".x.axis").call(axis_x.scale(scale_x))
    update()
    update_hover()
  }

  function zoomed_y() {
    var e_t = d3.event.transform
    var xy_t = d3.xyzoomTransform(g.select('rect.zoom-xy').node())
    var new_t = d3.xyzoomIdentity.translate(xy_t.x,e_t.y).scale(xy_t.kx,e_t.ky)
    g.select('rect.zoom-xy').property('__zoom', new_t)
    scale_y = d3.event.transform.rescaleY(base_scale_y)
    svg.select(".y.axis").call(axis_y.scale(scale_y))
    update()
    update_hover()
  }

  function update() {
    // possibly we should simplify the paths
    var min_x = scale_x.domain()[0]
    var max_x = scale_x.domain()[1]
    var cut_data = []
    var y_maximiser = function(prev, cur) {return (prev.y > cur.y) ? prev : cur}
    var y_minimiser = function(prev, cur) {return (prev.y < cur.y) ? prev : cur}
    for (var i=0; i<data.length; i++) {
      var i0 = bisect_x(data[i], min_x, 1)-1
      var i1 = bisect_x(data[i], max_x, 1)+1
      cut_data[i] = data[i].slice(i0, i1)
      var decimation = Math.floor(cut_data[i].length / (MAX_DISPLAY_POINTS / 2))
      if (decimation > 2) {
        var dec_data = []
        for (var j=0; j < cut_data[i].length; j+=decimation) {
          var p_max = cut_data[i].slice(j, j+decimation).reduce(y_maximiser)
          var p_min = cut_data[i].slice(j, j+decimation).reduce(y_minimiser)
          dec_data.push(p_min)
          dec_data.push(p_max)
        }
        cut_data[i] = dec_data
      }

      plotPaths[i].datum(cut_data[i])
    }
    line.x(d => scale_x(d.x).toFixed(2))
        .y(d => scale_y(d.y).toFixed(2))
    svg.selectAll('.line').attr('d', line)
  }

  function update_hover() {
    var x0 = scale_x.invert(d3.mouse(overlay.node())[0])
    var prev_f_y = null
    for (var i=0; i<data.length; i++) {
      if (data[i].length==0) return
      var index = bisect_x(data[i], x0, 1)
      var p0 = data[i][index-1]
      var p1 = data[i][index]
      var p = p1 && (x0-p0.x > p1.x-x0) ? p1 : p0

      var f_x = scale_x(p.x)
      var f_y = scale_y(p.y)
      crosshairs[i].attr('y1', f_y).attr('y2', f_y)
      lineFoci[i].select('circle').attr('cx', f_x).attr('cy', f_y)
      if (w - f_x < f_w+fontS/2) // no room on right for focus label
        f_x-=f_w+fontS/2
      else
        f_x+=fontS/2
      f_y-=fontS/2
      f_y = Math.min(Math.max(f_y, 0), h-fontS)
      if (prev_f_y!==null) {
        var vertdist = f_y-prev_f_y
        if (Math.abs(vertdist) < f_h) {
          var sign = (vertdist === 0) ? 1 : Math.sign(vertdist)
          sign = (prev_f_y === h-f_h) ? -1 : sign
          f_y = prev_f_y+sign*f_h
        }
      }
      lineFoci[i].select('rect').attr('x', f_x).attr('y', f_y)
      lineFoci[i].select('text').attr('x', f_x).attr('y', f_y).text(focusFormat(p.y))
      prev_f_y = f_y
      g.selectAll('.focus').style('display', null)
    }

    // vertical crosshair
    var fx_x = scale_x(x0)
    crosshairX.attr('x1', fx_x).attr('x2', fx_x)
    // horizontal position label
    var fx_x = Math.min(w-f_w+0.5, Math.max(0.5, fx_x - f_w/2))
    var fx_y = h
    focusX.select('rect').attr('x', fx_x).attr('y', fx_y)
    focusX.select('text').attr('x', fx_x).attr('y', fx_y).text(focusFormat(x0))
  }

  function wrap(text, width) {
      text.each(function () {
          var text = d3.select(this),
              words = text.text().split(/\s+/).reverse(),
              word,
              line = [],
              lineNumber = 0,
              lineHeight = 1.1, // ems
              x = text.attr("x"),
              y = text.attr("y"),
              dy = 0,
              tspan = text.text(null)
                          .append("tspan")
                          .attr("x", x)
                          .attr("y", y)
                          .attr("dy", dy + "em");
          while (word = words.pop()) {
              line.push(word);
              tspan.text(line.join(" "));
              if (tspan.node().getComputedTextLength() > width) {
                  line.pop();
                  tspan.text(line.join(" "));
                  line = [word];
                  tspan = text.append("tspan")
                              .attr("x", x)
                              .attr("y", y)
                              .attr("dy", ++lineNumber * lineHeight + dy + "em")
                              .text(word);
              }
          }
      });
  }
}
