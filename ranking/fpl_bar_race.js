// This script expects a global variable fplData (from fpl_managers_history.json)
// and renders a bar race chart of evolving ranks across all gameweeks

function transformFPLData(fplData) {
  // Collect all gameweeks
  const allGameweeks = new Set();
  const managers = [];
  for (const entryId in fplData) {
    const manager = fplData[entryId];
    managers.push({
      entryId,
      team_name: manager.team_name,
      player_name: manager.player_name,
      history: manager.history.current,
    });
    manager.history.current.forEach((gw) => allGameweeks.add(gw.event));
  }
  const sortedGameweeks = Array.from(allGameweeks).sort((a, b) => a - b);

  const frames = sortedGameweeks.map((gw) => {
    const frame = managers
      .map((m) => {
        const gwData = m.history.find((e) => e.event === gw);
        return {
          name: m.team_name,
          player: m.player_name,
          points: gwData ? gwData.total_points : null,
          round_points: gwData ? gwData.points : null,
        };
      })
      .filter((m) => m.points !== null);
    frame.sort((a, b) => a.points - b.points);
    return { gw, frame };
  });
  return frames;
}

function renderBarRace(frames) {
  const chartDom = document.getElementById("main");
  const myChart = echarts.init(chartDom);
  const updateFrequency = 1500; // Increased from 1500 to 2000ms for slower reordering
  let currentFrameLookup = {};
  let option = {
    grid: { top: 10, bottom: 30, left: 300, right: 250 }, // Increased left margin for long labels
    xAxis: {
      inverse: false,
      max: "dataMax",
      axisLabel: {
        formatter: function (n) {
          return n;
        },
      },
      minInterval: 1, // Prevents label overlap for integer points
    },
    yAxis: {
      type: "category",
      inverse: true,
      max: null, // Show all managers, not just top 10
      axisLabel: {
        show: true,
        fontSize: 14,
        formatter: function (teamName) {
          const info = currentFrameLookup[teamName];
          if (info) {
            return `${teamName} (${info.player})`;
          }
          return teamName;
        },
      },
      animationDuration: 500,
      animationDurationUpdate: 500,
    },
    series: [
      {
        realtimeSort: true,
        seriesLayoutBy: "column",
        type: "bar",
        itemStyle: {
          color: function (param) {
            // Assign color by final frame position for a nice spectrum
            if (!window.finalFrameColorMap) {
              // Build color map on first call
              const lastFrame = frames[frames.length - 1].frame;
              window.finalFrameColorMap = {};
              lastFrame.forEach((m, idx) => {
                // Evenly distribute hues across the spectrum
                const hue = Math.round((idx / lastFrame.length) * 360);
                window.finalFrameColorMap[m.name] = `hsl(${hue},70%,55%)`;
              });
            }
            return window.finalFrameColorMap[param.value[1]] || "#888";
          },
        },
        encode: { x: 0, y: 1 },
        label: {
          show: true,
          position: "right",
          valueAnimation: true,
          fontFamily: "monospace",
          formatter: function (params) {
            // Show total points, round points, and manager name to the right of the bar using currentFrameLookup
            const info = currentFrameLookup[params.value[1]];
            if (info) {
              return `${info.points} (GW: ${info.round_points}) - ${info.player}`;
            }
            return "";
          },
        },
      },
    ],
    animationDuration: 0,
    animationDurationUpdate: updateFrequency,
    animationEasing: "linear",
    animationEasingUpdate: "linear",
    graphic: {
      elements: [
        {
          type: "text",
          right: 160,
          bottom: 60,
          style: {
            text: "",
            font: "bolder 80px monospace",
            fill: "rgba(100, 100, 100, 0.25)",
          },
          z: 100,
        },
      ],
    },
  };

  let i = 0;
  function updateFrame(idx) {
    const frame = frames[idx];
    // Build lookup for yAxis label formatting
    currentFrameLookup = {};
    frame.frame.forEach((m) => {
      currentFrameLookup[m.name] = {
        player: m.player,
        points: m.points,
        round_points: m.round_points,
      };
    });
    option.dataset = {
      source: frame.frame.map((m) => [m.points, m.name, m.player]),
    };
    option.yAxis.data = frame.frame.map((m) => m.name);
    option.graphic.elements[0].style.text = "GW " + frame.gw;
    myChart.setOption(option);
  }
  updateFrame(0);
  for (let j = 1; j < frames.length; ++j) {
    setTimeout(() => updateFrame(j), j * updateFrequency);
  }
}

// Wait for fplData to be defined in the HTML
if (typeof fplData !== "undefined") {
  const frames = transformFPLData(fplData);
  renderBarRace(frames);
}
