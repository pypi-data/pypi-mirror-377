import React, { useState, useEffect, useRef } from 'react';
import { Card, Select, Space, Spin, message, Button, Tooltip, Empty } from 'antd';
import { Line } from '@ant-design/plots';
import { G2 } from "@ant-design/plots";



import { ReloadOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useLoading } from '../contexts/LoadingContext';
import { useNamespace } from '../contexts/NamespaceContext';
import QueueDetailsTableV2 from '../components/QueueDetailsTableV2';
import TimeRangeSelector from '../components/TimeRangeSelector';
import { getUserPreferences, setPreference, PREFERENCE_KEYS } from '../utils/userPreferences';

import dayjs from 'dayjs';
import axios from 'axios';

const { ChartEvent } = G2;

function QueueMonitor() {
  const { setLoading: setGlobalLoading } = useLoading();
  const { currentNamespace } = useNamespace();
  const [loading, setLoading] = useState(false);
  const [queues, setQueues] = useState([]);

  // 从本地存储恢复用户设置
  const preferences = getUserPreferences();
  const [selectedQueues, setSelectedQueues] = useState(
    preferences[PREFERENCE_KEYS.QUEUE_MONITOR_SELECTED_QUEUES] || []
  );
  const savedTimeRange = preferences[PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE] || '15m';
  const [timeRange, setTimeRange] = useState(savedTimeRange);

  // 只有当保存的时间范围是 'custom' 时，才恢复自定义时间范围
  const savedCustomRange = preferences[PREFERENCE_KEYS.QUEUE_MONITOR_CUSTOM_TIME_RANGE];
  const [customTimeRange, setCustomTimeRange] = useState(
    savedTimeRange === 'custom' && savedCustomRange
      ? [dayjs(savedCustomRange[0]), dayjs(savedCustomRange[1])]
      : null
  );
  const [chartData, setChartData] = useState([]);
  const [granularity, setGranularity] = useState('');
  const [sliderValues, setSliderValues] = useState([0, 1]); // slider控件的值范围

  // 用于防抖的 ref
  const fetchTimeoutRef = useRef(null);
  const isBrushingRef = useRef(false);
  const queueDetailsRef = useRef(null);

  // 使用 ref 追踪最新的 timeRange 和 customTimeRange
  const timeRangeRef = useRef(timeRange);
  const customTimeRangeRef = useRef(customTimeRange);

  // 每次状态更新时同步更新 ref
  useEffect(() => {
    timeRangeRef.current = timeRange;
    console.log('[QueueMonitor] timeRangeRef 更新为:', timeRange);
  }, [timeRange]);

  useEffect(() => {
    customTimeRangeRef.current = customTimeRange;
  }, [customTimeRange]);

  // 获取队列列表
  const fetchQueues = async () => {
    if (!currentNamespace) {
      return;
    }

    try {
      // 先调用 get_queues 获取指定命名空间的队列名称
      const response = await axios.get(`/api/queues/${currentNamespace}`);
      if (response.data && response.data.success) {
        const queueList = response.data.data;
        setQueues(queueList);

        // 如果有保存的选择，恢复之前的选择；否则默认选择前10个
        const savedQueues = preferences[PREFERENCE_KEYS.QUEUE_MONITOR_SELECTED_QUEUES];
        if (savedQueues && savedQueues.length > 0) {
          // 过滤掉不存在的队列
          const validQueues = savedQueues.filter(q => queueList.includes(q));
          if (validQueues.length > 0) {
            setSelectedQueues(validQueues);
          } else if (queueList.length > 0) {
            // 如果保存的队列都不存在了，选择前10个
            const defaultQueues = queueList.slice(0, 10);
            setSelectedQueues(defaultQueues);
            setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_SELECTED_QUEUES, defaultQueues);
          }
        } else if (selectedQueues.length === 0 && queueList.length > 0) {
          // 第一次使用，默认选择前10个
          const defaultQueues = queueList.slice(0, 10);
          setSelectedQueues(defaultQueues);
          setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_SELECTED_QUEUES, defaultQueues);
        }
      }
    } catch (error) {
      message.error('获取队列列表失败');
      console.error('Failed to fetch queues:', error);
    }
  };

  // 获取队列趋势数据
  const fetchQueueTimeline = async () => {
    if (!currentNamespace || selectedQueues.length === 0) {
      return;
    }

    setLoading(true);
    setGlobalLoading(true, '加载数据中...');
    try {
      // 使用 ref 中的最新值
      const currentTimeRange = timeRangeRef.current;
      const currentCustomTimeRange = customTimeRangeRef.current;

      const params = {
        namespace: currentNamespace,
        queues: selectedQueues,
        time_range: currentTimeRange,
      };

      // 如果有自定义时间范围
      if (currentCustomTimeRange) {
        params.start_time = currentCustomTimeRange[0].toISOString();
        params.end_time = currentCustomTimeRange[1].toISOString();
      }
      console.log('[QueueMonitor.fetchQueueTimeline] 请求参数:', params, 'currentTimeRange:', currentTimeRange, 'timeRange状态值:', timeRange);

      const response = await axios.post(`/api/data/queue-timeline/${currentNamespace}`, params);
      const { data, granularity: dataGranularity } = response.data;

      setChartData(data);
      setGranularity(dataGranularity);
      // 如果是刷选触发，获取新数据后重置 slider 为全范围
      // 这样新数据会完整显示
      setSliderValues([0, 1]);
    } catch (error) {
      message.error('获取队列趋势数据失败');
      console.error('Failed to fetch queue timeline:', error);
    } finally {
      setLoading(false);
      setGlobalLoading(false);
      isBrushingRef.current = false;
    }
  };

  // 初始化和命名空间改变时获取队列
  useEffect(() => {
    if (currentNamespace) {
      fetchQueues();
    }
  }, [currentNamespace]);

  // 当选择的队列或时间范围改变时，重新获取数据
  useEffect(() => {
    if (selectedQueues.length > 0) {
      console.log('触发数据更新 - timeRange:', timeRange, 'customTimeRange:', customTimeRange);

      // 清除之前的定时器
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }

      // 如果是刷选触发的自定义时间范围，延迟一点获取数据
      const delay = isBrushingRef.current ? 300 : 0;

      fetchTimeoutRef.current = setTimeout(() => {
        fetchQueueTimeline();
      }, delay);
    }

    // 清理函数
    return () => {
      if (fetchTimeoutRef.current) {
        clearTimeout(fetchTimeoutRef.current);
      }
    };
  }, [selectedQueues, timeRange, customTimeRange]);


  // 手动刷新
  const handleRefresh = () => {
    console.log('[QueueMonitor] 刷新时的timeRange:', timeRange, 'customTimeRange:', customTimeRange);
    console.log('[QueueMonitor] 刷新时的selectedQueues:', selectedQueues);
    fetchQueueTimeline();
    // 同时刷新队列详细信息表格
    if (queueDetailsRef.current) {
      queueDetailsRef.current.refresh();
    }
  };


  // 图表配置
  const chartConfig = {
    data: chartData,
    xField: (d) => new Date(d.time),
    yField: 'value',
    colorField: 'queue',  // 使用 colorField 替代 seriesField
    smooth: true,
    // 禁用动画以避免错误
    animate: false,
    meta: {
      value: {
        alias: '任务数',
      },
      time: {
        type: 'time',
        alias: '时间',
      },
    },
    scale: {
      time: {
        type: 'time',
      },
      y: { nice: true },
      // 定义不同队列的颜色
      color: {
        range: ['#5B8FF9', '#5AD8A6', '#5D7092', '#F6BD16', '#E8684A', '#6DC8EC', '#9270CA', '#FF9D4D', '#269A99', '#FF99C3']
      }
    },
    // point: {
    //   size: 3,
    //   shape: 'circle',
    // },
    style: {
      lineWidth: 2,
    },
    xAxis: {
      type: 'time',
      label: {
        autoRotate: true,
        formatter: (text) => {
          // text 可能是时间戳或ISO字符串，统一处理
          const date = dayjs(text);

          // 根据后端返回的粒度决定显示格式
          switch (granularity) {
            case 'second':
              // 秒级：显示时分秒
              return date.format('HH:mm:ss');

            case 'minute':
              // 分钟级：显示时分
              return date.format('HH:mm');

            case 'hour':
              // 小时级：显示日期和小时
              return date.format('MM-DD HH:00');

            case 'day':
              // 跨天：显示年月日
              return date.format('YYYY-MM-DD');

            default:
              // 默认显示日期和小时
              return date.format('MM-DD HH:mm');
          }
        },
      },
    },
    yAxis: {
      label: {
        formatter: (v) => `${v}`,
      },
      title: {
        text: '处理任务数',
        style: {
          fontSize: 14,
        },
      },
    },
    autoFit: true,
    interaction: {
      brushXFilter: true // 启用横向筛选
    },
    connectNulls: {
      connect: true,
      connectStroke: '#aaa',
    },
    legend: {
      position: 'top',
      itemName: {
        style: {
          fontSize: 12,
        },
      },
    },
    // 配置 tooltip 时间格式，使用24小时制
    tooltip: {
      title: (title) => {
        // 使用相同的时间格式化逻辑
        const date = dayjs(title.time);
        switch (granularity) {
          case 'second':
            return date.format('YYYY-MM-DD HH:mm:ss');
          case 'minute':
            return date.format('YYYY-MM-DD HH:mm:ss');
          case 'hour':
            return date.format('YYYY-MM-DD HH:mm');
          case 'day':
            return date.format('YYYY-MM-DD');
          default:
            return date.format('YYYY-MM-DD HH:mm');
        }
      }
    },
    style: {
      lineWidth: 2,
    },
    // 监听brush事件，实现框选后自动请求数据
    onReady: (plot) => {
      console.log('图表已准备就绪', plot);

      // 获取所有可用的事件
      const chart = plot.chart;

      chart.on("brush:filter", (e) => {
        console.log('Brush filter 事件:', e);

        // 获取刷选的数据范围
        if (e.data && e.data.selection) {
          const selection = e.data.selection;
          console.log('Selection 数据:', selection);

          // selection[0] 是选中的时间数组
          if (selection && selection[0] && selection[0].length > 0) {
            const selectedTimes = selection[0];

            // 获取选中时间的起止
            const startTime = dayjs(selectedTimes[0]);
            const endTime = dayjs(selectedTimes[selectedTimes.length - 1]);

            console.log('刷选范围:', startTime.format(), endTime.format());

            // 设置刷选标志
            isBrushingRef.current = true;

            // 更新UI状态，这会触发 useEffect 重新获取数据
            setTimeRange('custom');
            setCustomTimeRange([startTime, endTime]);

            // 保存刷选的时间范围到本地存储
            setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_CUSTOM_TIME_RANGE,
              [startTime.toISOString(), endTime.toISOString()]
            );
            setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE, 'custom');

            // 不需要手动更新 slider，fetchQueueTimeline 会处理
          }
        }
      });
    },
  };

  // 如果没有选择命名空间，显示提示
  if (!currentNamespace) {
    return (
      <Card style={{ minHeight: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <span>
              请先在右上角选择一个命名空间
              <br />
              <span style={{ color: '#999', fontSize: '12px' }}>
                选择命名空间后才能查看该空间的队列数据
              </span>
            </span>
          }
        />
      </Card>
    );
  }

  return (
    <Card>
      {/* 控制面板 */}
      <Space size="large" style={{ marginBottom: '24px' }} wrap>
        <div>
          <span style={{ marginRight: '8px' }}>选择队列：</span>
          <Select
            mode="multiple"
            style={{ width: 400 }}
            placeholder="请选择队列"
            value={selectedQueues}
            onChange={(value) => {
              setSelectedQueues(value);
              // 保存到本地存储
              setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_SELECTED_QUEUES, value);
            }}
            options={queues.map(q => ({ label: q, value: q }))}
            maxTagCount="responsive"
          />
        </div>

        <div>
          <span style={{ marginRight: '8px' }}>时间范围：</span>
          <TimeRangeSelector
            value={timeRange}
            onChange={(value) => {
              console.log('[QueueMonitor] TimeRangeSelector onChange - 新值:', value, '旧值:', timeRange);
              setTimeRange(value);
              if (value !== 'custom') {
                setCustomTimeRange(null);
                // 保存到本地存储
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE, value);
                console.log('[QueueMonitor] 已保存timeRange到localStorage:', value);
                // 清除自定义时间范围的记忆
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_CUSTOM_TIME_RANGE, null);
                // 验证保存是否成功
                setTimeout(() => {
                  const saved = getUserPreferences();
                  console.log('[QueueMonitor] 验证localStorage保存:', saved[PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE]);
                }, 100);
              }
            }}
            customValue={customTimeRange}
            onCustomChange={(dates) => {
              console.log('[QueueMonitor] onCustomChange 被调用, dates:', dates);
              if (dates && dates.length === 2) {
                setCustomTimeRange(dates);
                setTimeRange('custom');
                // 保存自定义时间范围到本地存储
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_CUSTOM_TIME_RANGE,
                  [dates[0].toISOString(), dates[1].toISOString()]
                );
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE, 'custom');
              } else if (dates === null) {
                // dates 为 null 时，说明是选择了预设时间，不需要做任何操作
                // TimeRangeSelector 的 onChange 已经处理了
                console.log('[QueueMonitor] onCustomChange - dates为null，跳过处理（预设时间已在onChange中处理）');
                setCustomTimeRange(null);
              } else {
                // 其他情况（可能是清空了选择）
                setCustomTimeRange(null);
                setTimeRange('15m');
                // 清除自定义时间范围
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_CUSTOM_TIME_RANGE, null);
                setPreference(PREFERENCE_KEYS.QUEUE_MONITOR_TIME_RANGE, '15m');
              }
            }}
          />
        </div>

        <Button
          icon={<ReloadOutlined spin={loading} />}
          onClick={handleRefresh}
          disabled={loading}
          type="primary"
        >
          {loading ? '刷新' : '刷新'}
        </Button>

        <Tooltip
          placement="bottomRight"
          title={
            <div style={{ fontSize: '12px' }}>
              <div style={{ marginBottom: '4px', fontWeight: 'bold' }}>操作提示：</div>
              <ul style={{ margin: '0 0 0 16px', paddingLeft: '0' }}>
                <li>鼠标按住左键横向拖动可刷选时间范围</li>
                <li>刷选后自动获取该时段的详细数据</li>
                <li>数据粒度根据时间范围自动调整</li>
                <li>点击图表空白处取消刷选</li>
              </ul>
            </div>
          }
        >
          <QuestionCircleOutlined style={{ fontSize: '16px', color: '#1890ff', cursor: 'help' }} />
        </Tooltip>
      </Space>

      {/* 图表 */}
      <div style={{ height: '240px', position: 'relative' }}>
        {chartData.length > 0 ? (
          <>
            <Line {...chartConfig} />
            {/* {loading && (
              <div style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(255, 255, 255, 0.8)',
                zIndex: 1000,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Spin size="large" tip="正在获取选定时间范围的详细数据..." />
              </div>
            )} */}
          </>
        ) : (
          <div style={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999'
          }}>
            {loading ? (
              <Spin size="large" tip="正在加载数据..." />
            ) : (
              selectedQueues.length === 0 ? '请选择队列' : '暂无数据'
            )}
          </div>
        )}
      </div>

      {/* 分隔线 */}
      {/* <Divider style={{ margin: '24px 0 16px' }} /> */}

      {/* 队列详细信息表格 */}
      <QueueDetailsTableV2
        ref={queueDetailsRef}
        autoRefresh={false}
        refreshInterval={10000}
        selectedQueues={selectedQueues}
        timeRange={timeRange}
        customTimeRange={customTimeRange}
      />
    </Card>
  );
}

export default QueueMonitor;