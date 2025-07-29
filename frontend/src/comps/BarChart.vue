<template>
  <Bar
    :data="chartData"
    :options="chartOptions"
  />
</template>

<script setup lang="ts">

  import { computed } from 'vue'
  import { Bar } from 'vue-chartjs'
  import {
    Chart,
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend,
  } from 'chart.js'
  import ChartDataLabels from 'chartjs-plugin-datalabels'


  Chart.register(
    BarElement,
    CategoryScale,
    LinearScale,
    Tooltip,
    Legend,
    ChartDataLabels,
  )

  const props = defineProps<{
    labels: string[]
    data: number[]
  }>()

  const chartData = computed(() => ({
    labels: props.labels,
    datasets: [
      {
        label: 'Ratio',
        backgroundColor: 'skyblue',
        data: props.data,
      },
    ],
  }))

  const chartOptions: any = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      },
      datalabels: {
        anchor: 'end',
        align: 'top',
        font: {
          size: 16,
          weight: 'bold',
        },
        formatter: (value: number) => `${value}%`,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 140,
        ticks: {
          stepSize: 20,
          font: {
            size: 16,
          },
        },
      },
      x: {
        ticks: {
          font: {
            size: 16,
          },
        },
      }
    },
  }

</script>
