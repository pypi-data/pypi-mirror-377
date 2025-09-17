import { useState, useEffect, useCallback } from 'react';
import { Card, Select, Spin, Empty, Space, Button, message } from 'antd';
import { Line } from '@ant-design/plots';
import { ReloadOutlined, ExpandOutlined } from '@ant-design/icons';
import { useNamespace } from '../contexts/NamespaceContext';
import dayjs from 'dayjs';
import axios from 'axios';

const { Option } = Select;

// 时间范围选项
const TIME_RANGES = {
  '15m': { label: '15分钟', minutes: 15 },
  '30m': { label: '30分钟', minutes: 30 },
  '1h': { label: '1小时', minutes: 60 },
  '3h': { label: '3小时', minutes: 180 },
  '6h': { label: '6小时', minutes: 360 },
  '12h': { label: '12小时', minutes: 720 },
  '24h': { label: '24小时', minutes: 1440 },
};

function QueueBacklogChart({ 
  height = 300, 
  showTitle = true, 
  defaultTimeRange = '1h',
  autoRefresh = true,
  refreshInterval = 60000, // 默认60秒刷新一次
  onExpand = null 
}) {
  const { currentNamespace } = useNamespace();
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState(defaultTimeRange);
  const [selectedQueues, setSelectedQueues] = useState([]);
  const [availableQueues, setAvailableQueues] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [lastUpdateTime, setLastUpdateTime] = useState(null);

  // 获取可用队列列表
  const fetchAvailableQueues = useCallback(async () => {
    try {
      const namespace = currentNamespace || 'default';
      const response = await axios.get(`/api/queues/${namespace}`);
      if (response.data.success) {
        const queues = response.data.data.map(q => q.name);
        setAvailableQueues(queues);
        
        // 默认选择前5个队列
        if (selectedQueues.length === 0 && queues.length > 0) {
          setSelectedQueues(queues.slice(0, 5));
        }
      }
    } catch (error) {
      console.error('Failed to fetch queues:', error);
    }
  }, [currentNamespace, selectedQueues.length]);

  // 获取队列积压数据
  const fetchBacklogData = useCallback(async () => {
    if (selectedQueues.length === 0) return;

    setLoading(true);
    try {
      const namespace = currentNamespace || 'default';
      const endTime = dayjs();
      const startTime = endTime.subtract(TIME_RANGES[timeRange].minutes, 'minute');
      
      const params = {
        namespace,
        queues: selectedQueues,
        time_range: timeRange,
        start_time: startTime.toISOString(),
        end_time: endTime.toISOString(),
        filters: [] // 不需要额外筛选
      };

      // 使用队列流量接口获取积压数据
      const response = await axios.post(`/api/data/queue-flow-rates/${namespace}`, params);
      
      if (response.data.success) {
        const { data } = response.data;
        
        // 转换数据格式，只保留pending数据作为积压量
        const backlogData = data
          .filter(item => item.metric === 'pending')
          .map(item => ({
            time: dayjs(item.time).format('HH:mm'),
            timestamp: item.time,
            queue: item.queue,
            value: item.value || 0,
            type: '积压量'
          }));
        
        setChartData(backlogData);
        setLastUpdateTime(dayjs());
      }
    } catch (error) {
      message.error('获取队列积压数据失败');
      console.error('Failed to fetch backlog data:', error);
    } finally {
      setLoading(false);
    }
  }, [currentNamespace, selectedQueues, timeRange]);

  // 初始化
  useEffect(() => {
    fetchAvailableQueues();
  }, [fetchAvailableQueues]);

  // 当选中队列变化时，获取数据
  useEffect(() => {
    if (selectedQueues.length > 0) {
      fetchBacklogData();
    }
  }, [selectedQueues, fetchBacklogData]);

  // 自动刷新
  useEffect(() => {
    if (!autoRefresh || selectedQueues.length === 0) return;

    const timer = setInterval(() => {
      fetchBacklogData();
    }, refreshInterval);

    return () => clearInterval(timer);
  }, [autoRefresh, refreshInterval, fetchBacklogData, selectedQueues.length]);

  // 图表配置
  const config = {
    data: chartData,
    xField: 'time',
    yField: 'value',
    seriesField: 'queue',
    height: height,
    smooth: true,
    animation: {
      appear: {
        animation: 'wave-in',
        duration: 1000,
      },
    },
    xAxis: {
      title: {
        text: '时间',
        style: { fontSize: 12 },
      },
      label: {
        autoRotate: true,
        autoHide: true,
      },
    },
    yAxis: {
      title: {
        text: '积压任务数',
        style: { fontSize: 12 },
      },
      min: 0,
      nice: true,
    },
    legend: {
      position: 'top-right',
      itemSpacing: 10,
    },
    tooltip: {
      shared: true,
      showCrosshairs: true,
      formatter: (datum) => {
        return {
          name: datum.queue,
          value: `${datum.value.toLocaleString()} 个任务`,
        };
      },
    },
    theme: {
      colors10: [
        '#5B8FF9',
        '#5AD8A6',
        '#5D7092',
        '#F6BD16',
        '#E8684A',
        '#6DC8EC',
        '#9270CA',
        '#FF9D4D',
        '#269A99',
        '#FF99C3',
      ],
    },
    // 添加告警线（可选）
    annotations: [
      {
        type: 'line',
        start: ['min', 1000],
        end: ['max', 1000],
        style: {
          stroke: '#ff9800',
          lineDash: [4, 4],
          lineWidth: 1,
        },
        text: {
          content: '警告线 (1000)',
          position: 'end',
          style: {
            textAlign: 'end',
            fontSize: 10,
            fill: '#ff9800',
          },
          offsetY: -5,
        },
      },
      {
        type: 'line',
        start: ['min', 5000],
        end: ['max', 5000],
        style: {
          stroke: '#f44336',
          lineDash: [4, 4],
          lineWidth: 1,
        },
        text: {
          content: '危险线 (5000)',
          position: 'end',
          style: {
            textAlign: 'end',
            fontSize: 10,
            fill: '#f44336',
          },
          offsetY: -5,
        },
      },
    ],
  };

  return (
    <Card 
      title={showTitle ? "队列积压趋势" : null}
      size="small"
      extra={
        <Space>
          {lastUpdateTime && (
            <span style={{ fontSize: 12, color: '#999' }}>
              更新于 {lastUpdateTime.format('HH:mm:ss')}
            </span>
          )}
          <Select
            value={timeRange}
            onChange={setTimeRange}
            style={{ width: 100 }}
            size="small"
          >
            {Object.entries(TIME_RANGES).map(([key, { label }]) => (
              <Option key={key} value={key}>{label}</Option>
            ))}
          </Select>
          <Select
            mode="multiple"
            placeholder="选择队列"
            value={selectedQueues}
            onChange={setSelectedQueues}
            style={{ minWidth: 200, maxWidth: 400 }}
            size="small"
            maxTagCount={2}
            maxTagTextLength={10}
          >
            {availableQueues.map(queue => (
              <Option key={queue} value={queue}>{queue}</Option>
            ))}
          </Select>
          <Button
            icon={<ReloadOutlined />}
            size="small"
            onClick={fetchBacklogData}
            loading={loading}
          />
          {onExpand && (
            <Button
              icon={<ExpandOutlined />}
              size="small"
              onClick={onExpand}
              title="展开详情"
            />
          )}
        </Space>
      }
    >
      <Spin spinning={loading}>
        {chartData.length > 0 ? (
          <Line {...config} />
        ) : (
          <Empty 
            description={selectedQueues.length === 0 ? "请选择要监控的队列" : "暂无数据"} 
            style={{ height: height, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}
          />
        )}
      </Spin>
    </Card>
  );
}

export default QueueBacklogChart;