(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var success = style.getPropertyValue('--success').trim();
  var danger = style.getPropertyValue('--danger').trim();

  // --- Chart: Module Pass Rate ---
  var chart1 = echarts.init(document.getElementById('chart-passrate'), null, { renderer: 'svg' });
  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['安全扫描', '身份认证', '协作通信', '技能市场', '沙箱执行', 'API扫描', 'A2A网关'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, formatter: '{value}%' }
    },
    series: [{
      name: '通过率',
      type: 'bar',
      barWidth: '50%',
      data: [
        { value: 100, itemStyle: { color: success } },
        { value: 100, itemStyle: { color: success } },
        { value: 75, itemStyle: { color: accent } },
        { value: 60, itemStyle: { color: accent } },
        { value: 100, itemStyle: { color: success } },
        { value: 100, itemStyle: { color: success } },
        { value: 50, itemStyle: { color: danger } }
      ],
      label: { show: true, position: 'top', color: ink, formatter: '{c}%' }
    }]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // --- Chart: Agent Eco Layers Coverage ---
  var chart2 = echarts.init(document.getElementById('chart-layers'), null, { renderer: 'svg' });
  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', appendToBody: true },
    legend: { data: ['当前覆盖度', '理想覆盖度'], textStyle: { color: muted }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['L1 基础设施', 'L2 身份层', 'L3 安全层', 'L4 传输层', 'L5 会话层', 'L6 技能层', 'L7 应用层'],
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      max: 10,
      axisLine: { show: false },
      splitLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted }
    },
    series: [
      {
        name: '当前覆盖度',
        type: 'bar',
        barWidth: '35%',
        data: [3, 5, 8, 6, 6, 5, 0],
        itemStyle: { color: accent },
        label: { show: true, position: 'top', color: ink }
      },
      {
        name: '理想覆盖度',
        type: 'bar',
        barWidth: '35%',
        data: [10, 10, 10, 10, 10, 10, 0],
        itemStyle: { color: 'rgba(148,163,184,0.2)' },
        barGap: '-100%',
        label: { show: false }
      }
    ]
  });
  window.addEventListener('resize', function() { chart2.resize(); });
})();
