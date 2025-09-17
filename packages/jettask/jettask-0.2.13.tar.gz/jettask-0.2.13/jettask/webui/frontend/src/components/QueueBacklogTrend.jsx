import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, Spin, Empty, Space, message, Row, Col, Statistic, Alert } from 'antd';
import { Line, Column } from '@ant-design/plots';
import { WarningOutlined } from '@ant-design/icons';
import { useNamespace } from '../contexts/NamespaceContext';
import dayjs from 'dayjs';
import axios from 'axios';

// 时间范围选项
const TIME_RANGES = {
  '15m': { label: '15分钟', minutes: 15, granularity: 'minute' },
  '30m': { label: '30分钟', minutes: 30, granularity: 'minute' },
  '1h': { label: '1小时', minutes: 60, granularity: 'minute' },
  '3h': { label: '3小时', minutes: 180, granularity: '5minute' },
  '6h': { label: '6小时', minutes: 360, granularity: '10minute' },
  '12h': { label: '12小时', minutes: 720, granularity: '30minute' },
  '24h': { label: '24小时', minutes: 1440, granularity: 'hour' },
  '3d': { label: '3天', minutes: 4320, granularity: 'hour' },
  '7d': { label: '7天', minutes: 10080, granularity: 'hour' },
};

// 告警阈值配置
const ALERT_THRESHOLDS = {
  warning: 1000,  // 警告阈值
  critical: 5000, // 严重阈值
};

function QueueBacklogTrend({
  height = 240,  // 默认高度改为240，与QueueDetail中的流量速率图表一致
  showTitle = true,
  defaultTimeRange = '1h',
  autoRefresh = true,
  refreshInterval = 60000,
  showStatistics = true,
  chartType = 'line', // 'line' or 'column'
  onAlertTriggered = null,
  selectedQueues: propSelectedQueues = null, // 可以从props传入选中的队列
}) {
  const { currentNamespace } = useNamespace();
  const [loading, setLoading] = useState(false);
  // 直接使用props中的defaultTimeRange，不使用内部状态
  const timeRange = defaultTimeRange;
  const [selectedQueues, setSelectedQueues] = useState(propSelectedQueues === null ? [] : propSelectedQueues || []);
  const [, setAvailableQueues] = useState([]);
  
  const [chartData, setChartData] = useState([]);
  const [isChartReady, setIsChartReady] = useState(false);
  const [statistics, setStatistics] = useState({
    total: 0,
    max: 0,
    avg: 0,
    trend: 'stable', // 'up', 'down', 'stable'
    alertQueues: [],
  });
  const [viewType] = useState(chartType);
  const [, setLastUpdateTime] = useState(null);

  // 计算统计信息
  const calculateStatistics = useCallback((data) => {
    if (!data || data.length === 0) {
      setStatistics({
        total: 0,
        max: 0,
        avg: 0,
        trend: 'stable',
        alertQueues: [],
      });
      return;
    }

    // 获取最新时间点的数据
    const latestTime = Math.max(...data.map(d => new Date(d.timestamp).getTime()));
    const latestData = data.filter(d => new Date(d.timestamp).getTime() === latestTime);

    // 计算总积压
    const total = latestData.reduce((sum, d) => sum + d.value, 0);

    // 计算最大值
    const max = Math.max(...data.map(d => d.value));

    // 计算平均值
    const avg = data.length > 0 ? data.reduce((sum, d) => sum + d.value, 0) / data.length : 0;

    // 分析趋势（比较最近和之前的数据）
    const timePoints = [...new Set(data.map(d => d.timestamp))].sort();
    let trend = 'stable';
    if (timePoints.length >= 2) {
      const recentTime = timePoints[timePoints.length - 1];
      const previousTime = timePoints[Math.max(0, timePoints.length - 6)]; // 对比5个时间点前

      const recentTotal = data
        .filter(d => d.timestamp === recentTime)
        .reduce((sum, d) => sum + d.value, 0);

      const previousTotal = data
        .filter(d => d.timestamp === previousTime)
        .reduce((sum, d) => sum + d.value, 0);

      const diff = recentTotal - previousTotal;
      const diffPercent = previousTotal > 0 ? (diff / previousTotal) * 100 : 0;

      if (diffPercent > 20) trend = 'up';
      else if (diffPercent < -20) trend = 'down';
    }

    // 检查告警队列
    const alertQueues = [];
    selectedQueues.forEach(queue => {
      const queueData = latestData.find(d => d.queue === queue);
      if (queueData) {
        if (queueData.value >= ALERT_THRESHOLDS.critical) {
          alertQueues.push({ queue, level: 'critical', value: queueData.value });
        } else if (queueData.value >= ALERT_THRESHOLDS.warning) {
          alertQueues.push({ queue, level: 'warning', value: queueData.value });
        }
      }
    });

    // 触发告警回调
    if (onAlertTriggered && alertQueues.length > 0) {
      onAlertTriggered(alertQueues);
    }

    setStatistics({
      total: Math.round(total),
      max: Math.round(max),
      avg: Math.round(avg),
      trend,
      alertQueues,
    });
  }, [selectedQueues, onAlertTriggered]);

  // 直接获取积压数据，不依赖selectedQueues状态
  const fetchBacklogDataDirectly = async (queueList) => {
    console.log('fetchBacklogDataDirectly called with:', queueList);
    const validQueues = queueList.filter(q => q != null && q !== '');
    console.log('validQueues:', validQueues);
    if (validQueues.length === 0) {
      console.log('No valid queues, returning early');
      return;
    }

    setLoading(true);
    setIsChartReady(false);
    try {
      const namespace = currentNamespace || 'default';

      const response = await axios.get(`/api/stream-backlog/${namespace}`, {
        params: {
          hours: Math.ceil(TIME_RANGES[timeRange].minutes / 60) || 1
        }
      });

      console.log('Backlog API Response:', response.status, response.data);

      if (response.data.success) {
        const data = response.data.data;
        const backlogData = [];
        
        if (data && Array.isArray(data)) {
          data.forEach(item => {
            backlogData.push({
              time: dayjs(item.created_at).format('HH:mm:ss'),
              timestamp: item.created_at,
              queue: item.stream_name,
              series: item.consumer_group || item.stream_name,
              value: item.backlog_unprocessed || 0,
              consumer_group: item.consumer_group,
            });
          });
        }

        console.log('Processed chart data:', backlogData);
        setChartData(backlogData);
        setTimeout(() => setIsChartReady(true), 100);

        if (backlogData.length > 0) {
          calculateStatistics(backlogData);
        } else {
          setStatistics({
            total: 0,
            max: 0,
            avg: 0,
            trend: 'stable',
            alertQueues: [],
          });
        }

        setLastUpdateTime(dayjs());
      }
    } catch (error) {
      console.error('Failed to fetch backlog data:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取队列积压数据（使用指定的队列列表）
  const fetchBacklogDataWithQueues = useCallback(async (queueList) => {
    return fetchBacklogDataDirectly(queueList);
  }, []);

  // 获取队列积压数据
  const fetchBacklogData = useCallback(async () => {
    return fetchBacklogDataWithQueues(selectedQueues);
  }, [selectedQueues, fetchBacklogDataWithQueues]);

  // 获取可用队列列表
  const fetchAvailableQueues = useCallback(async () => {
    console.log('fetchAvailableQueues called');
    try {
      const namespace = currentNamespace || 'default';
      console.log('Using namespace:', namespace);
      const response = await axios.get(`/api/queues/${namespace}`);
      console.log('Queues API response:', response);
      if (response.data.success) {
        // 过滤掉name为null或undefined的队列
        const queues = response.data.data;
        console.log('Raw queues data:', queues);
        setAvailableQueues(queues);

        // 如果没有通过props传入选中的队列，则根据propSelectedQueues判断选择策略
        if (!propSelectedQueues || propSelectedQueues.length === 0) {
          console.log('Processing queue selection logic...');
          // 如果propSelectedQueues为null，选择所有队列；否则选择积压最多的前5个队列
          const allQueues = response.data.data
            .filter(q => q && q.name != null && q.name !== '')
            .map(q => q.name);
          console.log('All available queues:', allQueues);
            
          const targetQueues = propSelectedQueues === null ? 
            allQueues : // 选择所有队列
            response.data.data
              .filter(q => q && q.name != null && q.name !== '')
              .sort((a, b) => (b.pending || 0) - (a.pending || 0))
              .slice(0, 5)
              .map(q => q.name); // 选择积压最多的前5个队列

          console.log('Target queues to select:', targetQueues);
          console.log('Current selectedQueues.length:', selectedQueues.length);

          if (selectedQueues.length === 0 && targetQueues.length > 0) {
            console.log('✅ Setting selectedQueues to:', targetQueues);
            setSelectedQueues(targetQueues);
            // 立即触发数据获取，使用新的队列列表
            setTimeout(async () => {
              console.log('🚀 Calling fetchBacklogDataWithQueues with:', targetQueues);
              // 直接调用数据获取逻辑，避免依赖循环
              await fetchBacklogDataDirectly(targetQueues);
            }, 100);
          } else {
            console.log('❌ Conditions not met for setting queues:', {
              selectedQueuesLength: selectedQueues.length,
              targetQueuesLength: targetQueues.length,
              propSelectedQueues,
              condition1: selectedQueues.length === 0,
              condition2: targetQueues.length > 0
            });
          }
        } else {
          console.log('Using provided propSelectedQueues:', propSelectedQueues);
        }
      }
    } catch (error) {
      console.error('Failed to fetch queues:', error);
    }
  }, [currentNamespace, selectedQueues.length, propSelectedQueues]);

  // 初始化
  useEffect(() => {
    fetchAvailableQueues();
  }, [fetchAvailableQueues]);

  // 处理通过props传入的选中队列
  useEffect(() => {
    if (propSelectedQueues && propSelectedQueues.length > 0) {
      setSelectedQueues(propSelectedQueues);
    }
  }, [propSelectedQueues]);

  // 当选中队列或时间范围变化时，获取数据
  useEffect(() => {
    console.log('selectedQueues changed:', selectedQueues, 'length:', selectedQueues.length);
    if (selectedQueues.length > 0) {
      console.log('Calling fetchBacklogData()');
      fetchBacklogData();
    } else {
      console.log('selectedQueues is empty, not calling fetchBacklogData');
    }
  }, [selectedQueues, timeRange, fetchBacklogData]);

  // 自动刷新
  useEffect(() => {
    if (!autoRefresh || selectedQueues.length === 0) return;

    const timer = setInterval(() => {
      fetchBacklogData();
    }, refreshInterval);

    return () => clearInterval(timer);
  }, [autoRefresh, refreshInterval, fetchBacklogData, selectedQueues.length]);

  // 图表配置
  const lineConfig = useMemo(() => {
    // 调试日志
    console.log('Creating lineConfig with chartData:', chartData);
    console.log('Chart data length:', chartData ? chartData.length : 0);

    // 确保数据有效
    if (!chartData || chartData.length === 0) {
      console.log('Chart data is empty, returning minimal config');
      return {
        data: [],
        xField: 'time',
        yField: 'value',
        height: height,
      };
    }

    // 验证数据格式
    const sampleData = chartData[0];
    console.log('Sample data item:', sampleData);
    console.log('Has time field:', 'time' in sampleData);
    console.log('Has value field:', 'value' in sampleData);
    console.log('Has series field:', 'series' in sampleData);

    // 定义颜色方案
    const colorPalette = [
      '#5B8FF9', // 蓝色
      '#5AD8A6', // 绿色
      '#5D7092', // 灰蓝色
      '#F6BD16', // 黄色
      '#E8684A', // 橙红色
      '#6DC8EC', // 天蓝色
      '#9270CA', // 紫色
      '#FF9D4D', // 橙色
      '#269A99', // 青色
      '#FF99C3', // 粉色
      '#7B9DF0', // 浅蓝色
      '#AAD977', // 黄绿色
      '#D97E84', // 玫瑰色
      '#9FD3E8', // 浅青色
      '#BFBFBF', // 灰色
    ];

    // 使用最基础的配置，避免复杂特性导致的错误
    const config = {
      data: chartData,
      xField: 'time',
      yField: 'value',
      seriesField: 'series',  // 关键：必须使用seriesField来区分不同的线
      colorField: 'series',  // 使用series字段来区分颜色
      smooth: true,  // 启用平滑曲线，避免突兀的转折
      animation: false,  // 关闭动画避免性能问题
      height: height, // 设置图表高度
      // 配置颜色 - 确保每个series有不同的颜色
      color: colorPalette,
      // 简单的点样式
      // point: {
      //   size: 3,
      //   shape: 'circle',
      // },
      // X轴配置 - 处理时间显示
      xAxis: {
        type: 'cat',  // 使用分类轴，因为时间已经格式化为字符串
        label: {
          autoRotate: true,
          autoHide: true,
          autoEllipsis: true,
        },
      },
      // Y轴配置  
      yAxis: {
        min: 0,
        label: {
          formatter: (v) => {
            return `${parseInt(v)}`;
          },
        },
      },
      legend: {
        position: 'top',
        itemName: {
          style: {
            fontSize: 12,
          },
        },
      },
      // tooltip: {
      //   showCrosshairs: true,
      //   shared: true,
      //   showMarkers: true,
      // },
      // 线条样式
      lineStyle: {
        lineWidth: 2,
      },
      // 连接空值
      connectNulls: true,
    };

    console.log('Final line config:', config);
    return config;
  }, [chartData, height]);

  const columnConfig = useMemo(() => {
    // 确保lineConfig有效
    if (!lineConfig || !lineConfig.data || lineConfig.data.length === 0) {
      return {
        data: [],
        xField: 'time',
        yField: 'value',
        height: height,
      };
    }

    return {
      ...lineConfig,
      isGroup: true,
      columnStyle: {
        radius: [4, 4, 0, 0],
      },
      // 柱状图特有的配置
      columnWidthRatio: 0.8,
      dodgePadding: 2,
    };
  }, [lineConfig, height]);

  // 趋势图标
  const getTrendIcon = () => {
    const { trend } = statistics;
    if (trend === 'up') return '↑';
    if (trend === 'down') return '↓';
    return '→';
  };

  const getTrendColor = () => {
    const { trend } = statistics;
    if (trend === 'up') return '#f50';
    if (trend === 'down') return '#52c41a';
    return '#1890ff';
  };

  return (
    <>
      <Card
        title={showTitle ? "队列积压监控" : null}
        size="small"
        styles={{
          body: {
            padding: showTitle ? '12px' : '0px',  // 无标题时不要padding
            height: 'auto',  // 让高度自适应
            overflow: 'hidden'
          }
        }}
        style={{
          // 如果没有标题和统计信息，设置固定高度
          height: !showTitle && !showStatistics ? height : 'auto',
        }}
      // extra={
      //   <Space>
      //     {lastUpdateTime && (
      //       <span style={{ fontSize: 12, color: '#999' }}>
      //         更新: {lastUpdateTime.format('HH:mm:ss')}
      //       </span>
      //     )}
      //     <Select
      //       value={timeRange}
      //       onChange={setTimeRange}
      //       style={{ width: 100 }}
      //       size="small"
      //     >
      //       {Object.entries(TIME_RANGES).map(([key, { label }]) => (
      //         <Option key={key} value={key}>{label}</Option>
      //       ))}
      //     </Select>
      //     {(!propSelectedQueues || propSelectedQueues.length === 0) && (
      //       <Select
      //         mode="multiple"
      //         placeholder="选择队列"
      //         value={selectedQueues.filter(q => q != null && q !== '')}
      //         onChange={(values) => {
      //           // 过滤掉null和空字符串
      //           const validValues = values.filter(v => v != null && v !== '');
      //           setSelectedQueues(validValues);
      //         }}
      //         style={{ minWidth: 200, maxWidth: 400 }}
      //         size="small"
      //         maxTagCount={2}
      //       >
      //         {availableQueues
      //           .filter(queue => queue != null && queue !== '')
      //           .map(queue => (
      //             <Option key={queue} value={queue}>{queue}</Option>
      //           ))}
      //       </Select>
      //     )}
      //     <Space.Compact size="small">
      //       <Button
      //         icon={<LineChartOutlined />}
      //         onClick={() => setViewType('line')}
      //         type={viewType === 'line' ? 'primary' : 'default'}
      //       />
      //       <Button
      //         icon={<BarChartOutlined />}
      //         onClick={() => setViewType('column')}
      //         type={viewType === 'column' ? 'primary' : 'default'}
      //       />
      //     </Space.Compact>
      //     <Button
      //       icon={<ReloadOutlined />}
      //       size="small"
      //       onClick={fetchBacklogData}
      //       loading={loading}
      //     />
      //   </Space>
      // }
      >
        {showStatistics && statistics.alertQueues.length > 0 && (
          <Alert
            message={
              <Space>
                <WarningOutlined />
                <span>
                  检测到 {statistics.alertQueues.length} 个队列积压超过阈值：
                  {statistics.alertQueues.map(({ queue, level, value }) => (
                    <span key={queue} style={{ marginLeft: 8 }}>
                      <strong>{queue}</strong>
                      <span style={{ color: level === 'critical' ? '#f50' : '#fa8c16' }}>
                        ({value.toLocaleString()})
                      </span>
                    </span>
                  ))}
                </span>
              </Space>
            }
            type={statistics.alertQueues.some(a => a.level === 'critical') ? 'error' : 'warning'}
            showIcon
            closable
            style={{ marginBottom: 16 }}
          />
        )}

        {showStatistics && (
          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={6}>
              <Statistic
                title="当前总积压"
                value={statistics.total}
                suffix="个"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="最大积压"
                value={statistics.max}
                suffix="个"
                valueStyle={{ color: statistics.max > ALERT_THRESHOLDS.critical ? '#f50' : undefined }}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="平均积压"
                value={statistics.avg}
                suffix="个"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="积压趋势"
                value={getTrendIcon()}
                valueStyle={{ color: getTrendColor(), fontSize: 24 }}
                prefix={
                  <span style={{ fontSize: 14, color: '#999' }}>
                    {statistics.trend === 'up' ? '上升' : statistics.trend === 'down' ? '下降' : '平稳'}
                  </span>
                }
              />
            </Col>
          </Row>
        )}

        <Spin spinning={loading} >
          {(() => {
            // 调试日志
            console.log('Rendering chart section, loading:', loading, 'chartData length:', chartData?.length);

            if (loading) {
              // 加载中，Spin组件会显示loading状态
              return null;
            }

            if (!chartData || chartData.length === 0) {
              // 无数据时显示空状态
              return (
                <div style={{
                  height: height,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Empty
                    description={selectedQueues.length === 0 ? "请选择要监控的队列" : "暂无数据"}
                    style={{ margin: 0 }}
                  />
                </div>
              );
            }

            // 有数据且图表准备就绪时才渲染
            if (!isChartReady) {
              console.log('Chart not ready yet, waiting...');
              return (
                <div style={{
                  height: height,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Spin />
                </div>
              );
            }

            console.log('Rendering chart with config:', lineConfig);
            return viewType === 'line' ? (
              <Line {...lineConfig} />
            ) : (
              <Column {...columnConfig} />
            );
          })()}
        </Spin>
      </Card>
    </>
  );
}

export default QueueBacklogTrend;