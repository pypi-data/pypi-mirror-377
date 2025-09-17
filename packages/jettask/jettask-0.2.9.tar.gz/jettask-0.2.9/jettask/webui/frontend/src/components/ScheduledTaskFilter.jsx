import React, { useState } from 'react';
import { Button, Popover, Form, Select, Input, Space, Tag, message } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';

const { Option } = Select;

// 定时任务可用的字段列表
const AVAILABLE_FIELDS = [
  { value: 'id', label: '任务ID', type: 'number' },
  { value: 'scheduler_id', label: '调度器ID', type: 'string' },
  { value: 'name', label: '任务名称', type: 'string' },
  { value: 'queue_name', label: '队列名称', type: 'string' },
  { value: 'schedule_type', label: '调度类型', type: 'enum', options: ['cron', 'interval', 'once'] },
  { value: 'is_active', label: '状态', type: 'boolean' },
  { value: 'description', label: '描述', type: 'string' },
  { value: 'last_run', label: '上次执行时间', type: 'datetime' },
  { value: 'next_run', label: '下次执行时间', type: 'datetime' },
  { value: 'created_at', label: '创建时间', type: 'datetime' },
  { value: 'task_data', label: '任务参数', type: 'json' },
  { value: 'tags', label: '标签', type: 'json' },
  { value: 'metadata', label: '元数据', type: 'json' },
];

// 操作符列表
const OPERATORS = {
  string: [
    { value: 'eq', label: '等于' },
    { value: 'ne', label: '不等于' },
    { value: 'contains', label: '包含' },
    { value: 'starts_with', label: '开始于' },
    { value: 'ends_with', label: '结束于' },
    { value: 'is_null', label: '为空' },
    { value: 'is_not_null', label: '不为空' },
  ],
  number: [
    { value: 'eq', label: '等于' },
    { value: 'ne', label: '不等于' },
    { value: 'gt', label: '大于' },
    { value: 'lt', label: '小于' },
    { value: 'gte', label: '大于等于' },
    { value: 'lte', label: '小于等于' },
    { value: 'is_null', label: '为空' },
    { value: 'is_not_null', label: '不为空' },
  ],
  datetime: [
    { value: 'gt', label: '晚于' },
    { value: 'lt', label: '早于' },
    { value: 'gte', label: '不早于' },
    { value: 'lte', label: '不晚于' },
    { value: 'is_null', label: '为空' },
    { value: 'is_not_null', label: '不为空' },
  ],
  enum: [
    { value: 'eq', label: '等于' },
    { value: 'ne', label: '不等于' },
    { value: 'in', label: '在列表中' },
    { value: 'not_in', label: '不在列表中' },
  ],
  boolean: [
    { value: 'eq', label: '等于' },
  ],
  json: [
    { value: 'contains', label: '包含文本' },
    { value: 'json_key_exists', label: '包含键名' },
    { value: 'json_path_value', label: 'JSON路径值' },
    { value: 'is_null', label: '为空' },
    { value: 'is_not_null', label: '不为空' },
  ],
};

function ScheduledTaskFilter({ filters, onFiltersChange }) {
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [selectedField, setSelectedField] = useState(null);
  const [selectedOperator, setSelectedOperator] = useState(null);
  const [disabledFilters, setDisabledFilters] = useState(new Set()); // 记录被禁用的筛选条件索引

  // 获取当前字段的类型
  const getFieldType = (fieldValue) => {
    const field = AVAILABLE_FIELDS.find(f => f.value === fieldValue);
    return field ? field.type : 'string';
  };

  // 获取当前字段的选项（用于枚举类型）
  const getFieldOptions = (fieldValue) => {
    const field = AVAILABLE_FIELDS.find(f => f.value === fieldValue);
    return field && field.options ? field.options : [];
  };

  // 添加筛选条件
  const handleAddFilter = () => {
    form.validateFields().then(values => {
      const newFilter = {
        id: Date.now(), // 添加唯一ID
        field: values.field,
        operator: values.operator,
        value: values.value,
        enabled: true, // 默认启用
      };

      // 处理特殊操作符
      if (values.operator === 'is_null' || values.operator === 'is_not_null') {
        newFilter.value = null;
      } else if (values.operator === 'in' || values.operator === 'not_in') {
        // 如果是枚举类型的多选
        if (getFieldType(values.field) === 'enum') {
          newFilter.value = values.value; // 已经是数组
        } else {
          // 普通文本，用逗号分隔
          newFilter.value = values.value.split(',').map(v => v.trim());
        }
      } else if (getFieldType(values.field) === 'boolean') {
        // 布尔类型转换
        newFilter.value = values.value === 'true';
      }

      const updatedFilters = [...(filters || []), newFilter];
      onFiltersChange(updatedFilters);
      
      // 重置表单
      form.resetFields();
      setSelectedField(null);
      setSelectedOperator(null);
      setVisible(false);
      message.success('筛选条件已添加');
    });
  };

  // 切换筛选条件的启用/禁用状态
  const handleToggleFilter = (index) => {
    const updatedFilters = [...filters];
    updatedFilters[index] = {
      ...updatedFilters[index],
      enabled: !updatedFilters[index].enabled
    };
    onFiltersChange(updatedFilters);
  };

  // 删除筛选条件
  const handleRemoveFilter = (index) => {
    const updatedFilters = filters.filter((_, i) => i !== index);
    onFiltersChange(updatedFilters);
    message.success('筛选条件已删除');
  };

  // 渲染筛选条件标签
  const renderFilterTag = (filter, index) => {
    const field = AVAILABLE_FIELDS.find(f => f.value === filter.field);
    const fieldLabel = field ? field.label : filter.field;
    
    const operator = OPERATORS[getFieldType(filter.field)]?.find(op => op.value === filter.operator);
    const operatorLabel = operator ? operator.label : filter.operator;
    
    let valueLabel = filter.value;
    if (filter.operator === 'is_null' || filter.operator === 'is_not_null') {
      valueLabel = '';
    } else if (Array.isArray(filter.value)) {
      valueLabel = filter.value.join(', ');
    } else if (typeof filter.value === 'boolean') {
      valueLabel = filter.value ? '是' : '否';
    }
    
    const tagLabel = `${fieldLabel} ${operatorLabel} ${valueLabel}`.trim();
    const isDisabled = filter.enabled === false;
    
    return (
      <Tag
        key={index}
        closable
        onClose={() => handleRemoveFilter(index)}
        onClick={() => handleToggleFilter(index)}
        style={{ 
          margin: 0,
          height: '24px',
          lineHeight: '22px',
          display: 'inline-flex',
          alignItems: 'center',
          cursor: 'pointer',
          opacity: isDisabled ? 0.5 : 1,
          textDecoration: isDisabled ? 'line-through' : 'none',
          backgroundColor: isDisabled ? '#f5f5f5' : undefined,
          borderStyle: isDisabled ? 'dashed' : 'solid',
        }}
        color={isDisabled ? 'default' : undefined}
      >
        {tagLabel}
      </Tag>
    );
  };

  // 渲染值输入组件
  const renderValueInput = () => {
    if (!selectedField) return null;
    
    const fieldType = getFieldType(selectedField);
    const needsValue = selectedOperator !== 'is_null' && selectedOperator !== 'is_not_null';
    
    if (!needsValue) return null;
    
    if (fieldType === 'enum') {
      const options = getFieldOptions(selectedField);
      if (selectedOperator === 'in' || selectedOperator === 'not_in') {
        return (
          <Form.Item
            name="value"
            label="值"
            rules={[{ required: true, message: '请选择值' }]}
          >
            <Select mode="multiple" placeholder="选择多个值">
              {options.map(opt => (
                <Option key={opt} value={opt}>{opt}</Option>
              ))}
            </Select>
          </Form.Item>
        );
      } else {
        return (
          <Form.Item
            name="value"
            label="值"
            rules={[{ required: true, message: '请选择值' }]}
          >
            <Select placeholder="选择值">
              {options.map(opt => (
                <Option key={opt} value={opt}>{opt}</Option>
              ))}
            </Select>
          </Form.Item>
        );
      }
    } else if (fieldType === 'boolean') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请选择值' }]}
        >
          <Select placeholder="选择值">
            <Option value="true">是</Option>
            <Option value="false">否</Option>
          </Select>
        </Form.Item>
      );
    } else if (fieldType === 'number') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请输入值' }]}
        >
          <Input type="number" placeholder="输入数值" />
        </Form.Item>
      );
    } else if (fieldType === 'datetime') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请输入值' }]}
        >
          <Input 
            placeholder="格式: YYYY-MM-DD HH:mm:ss" 
            title="请输入日期时间，格式: YYYY-MM-DD HH:mm:ss"
          />
        </Form.Item>
      );
    } else if (fieldType === 'json') {
      // JSON类型的输入
      let label = '搜索内容';
      let placeholder = '输入搜索内容';
      let extra = '';
      
      if (selectedOperator === 'json_key_exists') {
        label = '键名';
        placeholder = '输入要查找的键名';
        extra = '检查JSON中是否存在指定的键';
      } else if (selectedOperator === 'json_path_value') {
        label = 'JSON路径和值';
        placeholder = '路径=值，如：$.user_id=123 或 $.kwargs.message=test';
        extra = '使用JSON路径语法，格式：路径=值。支持嵌套路径如 $.kwargs.user_id';
      } else if (selectedOperator === 'contains') {
        label = '搜索文本';
        placeholder = '输入要搜索的文本内容';
        extra = '在JSON数据中搜索包含此文本的任务';
      }
      
      return (
        <Form.Item
          name="value"
          label={label}
          rules={[{ required: true, message: `请输入${label}` }]}
          extra={extra}
        >
          <Input.TextArea 
            placeholder={placeholder}
            rows={2}
            spellCheck={false}
          />
        </Form.Item>
      );
    } else {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请输入值' }]}
        >
          <Input placeholder={selectedOperator === 'in' || selectedOperator === 'not_in' ? '多个值用逗号分隔' : '输入值'} />
        </Form.Item>
      );
    }
  };

  const filterContent = (
    <div style={{ width: 350 }}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleAddFilter}
      >
        <Form.Item
          name="field"
          label="字段"
          rules={[{ required: true, message: '请选择字段' }]}
        >
          <Select
            placeholder="选择字段"
            onChange={(value) => {
              setSelectedField(value);
              setSelectedOperator(null);
              form.setFieldsValue({ operator: undefined, value: undefined });
            }}
          >
            {AVAILABLE_FIELDS.map(field => (
              <Option key={field.value} value={field.value}>
                {field.label}
              </Option>
            ))}
          </Select>
        </Form.Item>
        
        {selectedField && (
          <Form.Item
            name="operator"
            label="操作符"
            rules={[{ required: true, message: '请选择操作符' }]}
          >
            <Select
              placeholder="选择操作符"
              onChange={(value) => {
                setSelectedOperator(value);
                form.setFieldsValue({ value: undefined });
              }}
            >
              {OPERATORS[getFieldType(selectedField)]?.map(op => (
                <Option key={op.value} value={op.value}>
                  {op.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
        )}
        
        {renderValueInput()}
        
        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              添加筛选条件
            </Button>
            <Button onClick={() => {
              setVisible(false);
              form.resetFields();
              setSelectedField(null);
              setSelectedOperator(null);
            }}>
              取消
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </div>
  );

  return (
    <div style={{ 
      display: 'inline-flex', 
      alignItems: 'center', 
      flexWrap: 'wrap', 
      gap: '8px',
      verticalAlign: 'middle'
    }}>
      {filters && filters.map((filter, index) => renderFilterTag(filter, index))}
      
      <Popover
        content={filterContent}
        title="添加筛选条件"
        trigger="click"
        open={visible}
        onOpenChange={setVisible}
        placement="bottomLeft"
      >
        <Button 
          type="dashed" 
          icon={<PlusOutlined />}
          size="small"
          style={{ 
            height: '24px', 
            padding: '0 8px',
            display: 'inline-flex', 
            alignItems: 'center',
            lineHeight: '22px',
            verticalAlign: 'middle'
          }}
        >
          Add Filter
        </Button>
      </Popover>
    </div>
  );
}

export default ScheduledTaskFilter;