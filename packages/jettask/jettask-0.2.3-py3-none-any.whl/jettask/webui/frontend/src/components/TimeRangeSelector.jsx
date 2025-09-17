import { useState, useEffect } from 'react';
import { DatePicker } from 'antd';
import dayjs from 'dayjs';
import './TimeRangeSelector.css';

const { RangePicker } = DatePicker;

// 预设时间范围选项
const PRESET_RANGES = {
  '最近15分钟': () => [dayjs().subtract(15, 'minute'), dayjs()],
  '最近30分钟': () => [dayjs().subtract(30, 'minute'), dayjs()],
  '最近1小时': () => [dayjs().subtract(1, 'hour'), dayjs()],
  '最近3小时': () => [dayjs().subtract(3, 'hour'), dayjs()],
  '最近6小时': () => [dayjs().subtract(6, 'hour'), dayjs()],
  '最近12小时': () => [dayjs().subtract(12, 'hour'), dayjs()],
  '最近24小时': () => [dayjs().subtract(24, 'hour'), dayjs()],
  '最近7天': () => [dayjs().subtract(7, 'day'), dayjs()],
  '最近30天': () => [dayjs().subtract(30, 'day'), dayjs()],
};

// 时间范围值映射
const TIME_RANGE_MAP = {
  '最近15分钟': '15m',
  '最近30分钟': '30m',
  '最近1小时': '1h',
  '最近3小时': '3h',
  '最近6小时': '6h',
  '最近12小时': '12h',
  '最近24小时': '24h',
  '最近7天': '7d',
  '最近30天': '30d',
};

// 反向映射，从值到标签
const VALUE_TO_LABEL_MAP = Object.fromEntries(
  Object.entries(TIME_RANGE_MAP).map(([label, value]) => [value, label])
);

function TimeRangeSelector({ 
  value, 
  onChange, 
  customValue,
  onCustomChange,
  style = {},
  ...props 
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [presetLabel, setPresetLabel] = useState(
    value !== 'custom' && VALUE_TO_LABEL_MAP[value] ? VALUE_TO_LABEL_MAP[value] : null
  );
  
  // 当外部value改变时，更新预设标签
  useEffect(() => {
    if (value !== 'custom' && VALUE_TO_LABEL_MAP[value]) {
      setPresetLabel(VALUE_TO_LABEL_MAP[value]);
    } else if (value === 'custom') {
      setPresetLabel(null);
    }
  }, [value]);
  
  // 处理RangePicker变化
  const handleRangeChange = (dates) => {
    console.log('[TimeRangeSelector] handleRangeChange 被调用, dates:', dates);
    if (!dates || dates.length !== 2) {
      console.log('[TimeRangeSelector] dates 无效，返回');
      return;
    }
    
    const [start, end] = dates;
    
    // 检查是否匹配预设时间范围
    let matchedPreset = null;
    for (const [label, getRangeFn] of Object.entries(PRESET_RANGES)) {
      const [presetStart, presetEnd] = getRangeFn();
      // 允许2秒的误差
      if (
        Math.abs(start.diff(presetStart, 'second')) <= 2 &&
        Math.abs(end.diff(presetEnd, 'second')) <= 2
      ) {
        matchedPreset = label;
        break;
      }
    }
    
    console.log('[TimeRangeSelector] handleRangeChange - matchedPreset:', matchedPreset, 'start:', start.format(), 'end:', end.format());
    
    if (matchedPreset) {
      // 匹配到预设
      setPresetLabel(matchedPreset);
      const presetValue = TIME_RANGE_MAP[matchedPreset];
      console.log('[TimeRangeSelector] 设置预设值:', presetValue, '调用 onChange');
      onChange(presetValue);
      onCustomChange(null);
    } else {
      // 自定义时间范围
      setPresetLabel(null);
      console.log('[TimeRangeSelector] 设置自定义时间范围');
      onChange('custom');
      onCustomChange(dates);
    }
  };
  
  // 获取RangePicker的值
  const getRangePickerValue = () => {
    if (value === 'custom' && customValue) {
      return customValue;
    }
    // 预设时返回空，让RangePicker不显示具体时间
    return undefined;
  };
  
  return (
    <div className="time-range-selector-wrapper" style={{ position: 'relative', display: 'inline-block', ...style }}>
      <RangePicker
        showTime
        format="YYYY-MM-DD HH:mm:ss"
        value={getRangePickerValue()}
        onChange={handleRangeChange}
        placeholder={['开始时间', '结束时间']}
        presets={Object.entries(PRESET_RANGES).map(([label, getRangeFn]) => ({
          label,
          value: getRangeFn(),
        }))}
        style={{ width: 360 }}
        open={isOpen}
        onOpenChange={setIsOpen}
        allowClear={false}
        {...props}
      />
      
      {/* 预设标签覆盖层 */}
      {presetLabel && !isOpen && (
        <div 
          className="preset-label-overlay"
          onClick={() => setIsOpen(true)}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            paddingLeft: 11,
            paddingRight: 35,
            backgroundColor: '#fff',
            border: '1px solid #d9d9d9',
            borderRadius: 6,
            cursor: 'pointer',
            zIndex: 1,
          }}
        >
          <span style={{ color: 'rgba(0, 0, 0, 0.88)' }}>{presetLabel}</span>
        </div>
      )}
    </div>
  );
}

export default TimeRangeSelector;