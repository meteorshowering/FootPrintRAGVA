import * as d3 from 'd3';
import axios from 'axios';
import { graphConnectionManager } from '../utils/graphConnection';

export function createMapViewLogic() {
  return {
    data() {
      return {
        points: [],
        xScale: null,
        yScale: null,
        svgWidth: 0,
        svgHeight: 0,
        zoomTransform: null,
        zoomBehavior: null,
        contentGroup: null,
        showDensityMap: false,
        useNewDataFormat: false,
      };
    },

    methods: {
      async loadData(
        dataFile = '/enhanced_figures_with_coordinates.json',
        useNewFormat = false
      ) {
        try {
          const response = await axios.get(dataFile);
          this.points = this.processDataPoints(response.data, useNewFormat);
          this.drawPoints();
        } catch (error) {
          console.error('加载数据失败:', error);
        }
      },

      processDataPoints(data, useNewFormat = false) {
        if (useNewFormat) {
          return data.map(item => ({
            ...item,
            x: item.coordinates_2d ? item.coordinates_2d[0] : 0,
            y: item.coordinates_2d ? item.coordinates_2d[1] : 0,
          }));
        }

        return data;
      },

      drawPoints() {
        const svg = d3.select(this.$refs.svg);
        svg.selectAll('*').remove();

        if (!this.points || this.points.length === 0) return;

        const xExtent = d3.extent(this.points, d => d.x);
        const yExtent = d3.extent(this.points, d => d.y);

        const container = this.$el;
        this.svgWidth = container.clientWidth;
        this.svgHeight = container.clientHeight;

        const margin = 10;
        const width = this.svgWidth - margin * 2;
        const height = this.svgHeight - margin * 2;

        this.xScale = d3.scaleLinear()
          .domain(xExtent)
          .range([0, width]);

        this.yScale = d3.scaleLinear()
          .domain(yExtent)
          .range([height, 0]);

        this.contentGroup = svg.append('g').attr('class', 'content-group');

        this.zoomBehavior = d3.zoom()
          .scaleExtent([0.2, 5])
          .translateExtent([
            [-width * 3, -height * 3],
            [width * 4, height * 4],
          ])
          .on('zoom', (event) => {
            this.zoomTransform = event.transform;
            this.contentGroup.attr('transform', event.transform);
          });

        svg.call(this.zoomBehavior);

        const initialScale = Math.min(
          0.8,
          (this.svgWidth / width) * 0.9,
          (this.svgHeight / height) * 0.9
        );

        const initialX = (this.svgWidth - width * initialScale) / 2;
        const initialY = (this.svgHeight - height * initialScale) / 2;

        const initialTransform = d3.zoomIdentity
          .translate(initialX, initialY)
          .scale(initialScale);

        svg.call(this.zoomBehavior.transform, initialTransform);

        if (this.showDensityMap) {
          this.drawDensityMap(this.contentGroup);
        }

        const radius = Math.min(width, height) / 100;

        this.contentGroup
          .selectAll('circle')
          .data(this.points)
          .enter()
          .append('circle')
          .attr('cx', d => this.xScale(d.x))
          .attr('cy', d => this.yScale(d.y))
          .attr('r', radius)
          .attr('fill', 'blue')
          .attr('stroke', 'white')
          .attr('stroke-width', 1)
          .on('click', (event, d) => this.selectDataPoint(d));
      },

        selectDataPoint(point) {
        console.log('点击了数据点:', point);
        this.$store.dispatch('selectDataPoint', point);

        if (this.xScale && this.yScale) {
            graphConnectionManager.initializeAndDraw(
            this.$refs.svg,
            this.xScale,
            this.yScale,
            this.useNewDataFormat,
            point.id
            );
        }
        },

      async drawConnections() {
        if (this.xScale && this.yScale) {
          await graphConnectionManager.initializeAndDraw(
            this.$refs.svg,
            this.xScale,
            this.yScale,
            this.useNewDataFormat
          );
        }
      },

      clearConnections() {
        graphConnectionManager.clearConnections(this.$refs.svg);
      },

      toggleDensityMap() {
        this.showDensityMap = !this.showDensityMap;
        this.drawPoints();
      },

      toggleDataFormat() {
        this.useNewDataFormat = !this.useNewDataFormat;

        this.loadData(
          this.useNewDataFormat
            ? '/scientific_rag_embeddings_2d_papercollection.json'
            : '/scientific_rag_embeddings_2d.json',
          this.useNewDataFormat
        );
      },

      handleResize() {
        if (this.points.length > 0) {
          this.drawPoints();
        }
      },

      drawDensityMap(contentGroup) {
        const scaledPoints = this.points.map(d => [
          this.xScale(d.x),
          this.yScale(d.y),
        ]);

        const density = d3.contourDensity()
          .x(d => d[0])
          .y(d => d[1])
          .size([this.svgWidth, this.svgHeight])
          .bandwidth(30)
          .thresholds(20);

        const contours = density(scaledPoints);

        if (!contours || contours.length === 0) return;

        const color = d3.scaleSequential(d3.interpolateBlues)
          .domain([0, d3.max(contours, d => d.value)]);

        contentGroup
          .selectAll('path.density')
          .data(contours)
          .enter()
          .append('path')
          .attr('class', 'density')
          .attr('d', d3.geoPath())
          .attr('fill', d => color(d.value))
          .attr('opacity', 0.6)
          .attr('stroke', 'none')
          .on('mouseover', function (event, d) {
            d3.select(this).attr('opacity', 0.8);

            d3.selectAll('.tooltip').remove();

            d3.select('body')
              .append('div')
              .attr('class', 'tooltip')
              .style('position', 'absolute')
              .style('background', 'white')
              .style('padding', '5px')
              .style('border', '1px solid #ccc')
              .style('left', `${event.pageX + 10}px`)
              .style('top', `${event.pageY}px`)
              .html(`密度值: ${d.value.toFixed(4)}`);
          })
          .on('mouseout', function () {
            d3.select(this).attr('opacity', 0.6);
            d3.selectAll('.tooltip').remove();
          })
          .on('click', (event, d) => {
            const bounds = d3.geoBounds(d);
            const x0 = bounds[0][0];
            const y0 = bounds[0][1];
            const x1 = bounds[1][0];
            const y1 = bounds[1][1];

            const dx = x1 - x0;
            const dy = y1 - y0;

            const scale = 0.9 / Math.max(dx / this.svgWidth, dy / this.svgHeight);
            const translate = [
              this.svgWidth / 2 - scale * (x0 + dx / 2),
              this.svgHeight / 2 - scale * (y0 + dy / 2),
            ];

            d3.select(this.$refs.svg)
              .transition()
              .duration(500)
              .call(
                this.zoomBehavior.transform,
                d3.zoomIdentity.translate(...translate).scale(scale)
              );
          });
      },
    },

    mounted() {
      this.loadData();
      window.addEventListener('resize', this.handleResize);
    },

    beforeUnmount() {
      window.removeEventListener('resize', this.handleResize);
    },
  };
}