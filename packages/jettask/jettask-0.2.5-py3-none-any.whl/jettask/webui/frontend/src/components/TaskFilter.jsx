import React, { useState } from 'react';
import { Button, Popover, Form, Select, Input, Space, Tag, message } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';

const { Option } = Select;

// 可用的字段列表
const AVAILABLE_FIELDS = [
  { value: 'id', label: '任务ID', type: 'string' },
  { value: 'task_name', label: '任务名称', type: 'string' },
  { value: 'consumer_group', label: '消费者组', type: 'string' },
  { value: 'status', label: '状态', type: 'enum', options: ['pending', 'running', 'success', 'error', 'rejected'] },
  { value: 'worker_id', label: 'Worker ID', type: 'string' },
  { value: 'task_data', label: '任务参数(JSON)', type: 'json' },
  { value: 'result', label: '执行结果(JSON)', type: 'json' },
  { value: 'created_at', label: '创建时间', type: 'datetime' },
  { value: 'started_at', label: '开始时间', type: 'datetime' },
  { value: 'completed_at', label: '完成时间', type: 'datetime' },
  { value: 'retry_count', label: '重试次数', type: 'number' },
  { value: 'priority', label: '优先级', type: 'number' },
  { value: 'max_retry', label: '最大重试次数', type: 'number' },
  { value: 'error_message', label: '错误信息', type: 'string' },
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
  json: [
    { value: 'contains', label: '包含文本' },
    { value: 'json_key_exists', label: '包含键名' },
    { value: 'json_path_value', label: 'JSON路径值' },
    { value: 'is_null', label: '为空' },
    { value: 'is_not_null', label: '不为空' },
  ],
};

function TaskFilter({ filters, onFiltersChange }) {
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
    } else if (filter.operator === 'json_key_exists') {
      valueLabel = `键: ${filter.value}`;
    } else if (filter.operator === 'json_path_value') {
      // 显示更友好的格式
      if (filter.value && filter.value.includes('=')) {
        const [path, val] = filter.value.split('=', 2);
        valueLabel = `${path} = ${val}`;
      }
    }

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
        {fieldLabel} {operatorLabel} {valueLabel}
      </Tag>
    );
  };

  // 渲染值输入组件
  const renderValueInput = () => {
    if (!selectedField || !selectedOperator) return null;
    
    // 如果是空值判断，不需要输入值
    if (selectedOperator === 'is_null' || selectedOperator === 'is_not_null') {
      return null;
    }

    const fieldType = getFieldType(selectedField);
    const fieldOptions = getFieldOptions(selectedField);

    // 枚举类型的多选
    if (fieldType === 'enum' && (selectedOperator === 'in' || selectedOperator === 'not_in')) {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请选择值' }]}
        >
          <Select mode="multiple" placeholder="选择值">
            {fieldOptions.map(opt => (
              <Option key={opt} value={opt}>{opt}</Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    // 枚举类型的单选
    if (fieldType === 'enum') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请选择值' }]}
        >
          <Select placeholder="选择值">
            {fieldOptions.map(opt => (
              <Option key={opt} value={opt}>{opt}</Option>
            ))}
          </Select>
        </Form.Item>
      );
    }

    // 日期时间类型
    if (fieldType === 'datetime') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请输入值' }]}
        >
          <Input type="datetime-local" />
        </Form.Item>
      );
    }

    // 数字类型
    if (fieldType === 'number') {
      return (
        <Form.Item
          name="value"
          label="值"
          rules={[{ required: true, message: '请输入值' }]}
        >
          <Input type="number" placeholder="输入数字" />
        </Form.Item>
      );
    }

    // JSON类型
    if (fieldType === 'json') {
      // 根据不同的操作符显示不同的输入提示
      let label = '搜索内容';
      let placeholder = '输入搜索内容';
      let extra = '';
      
      if (selectedOperator === 'json_key_exists') {
        label = '键名';
        placeholder = '输入要查找的键名，如：user_id';
        extra = '检查JSON中是否存在指定的键';
      } else if (selectedOperator === 'json_path_value') {
        label = 'JSON路径和值';
        placeholder = '路径=值，如：$.user_id=123 或 $.data.status=active';
        extra = '使用JSON路径语法，格式：路径=值。支持嵌套路径如 $.data.user.name';
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
            spellCheck={false}  // 关闭拼写检查，避免JSON输入时的红线
          />
        </Form.Item>
      );
    }

    // 默认文本输入
    return (
      <Form.Item
        name="value"
        label="值"
        rules={[{ required: true, message: '请输入值' }]}
        extra={
          (selectedOperator === 'in' || selectedOperator === 'not_in') 
            ? '多个值用逗号分隔' : null
        }
      >
        <Input placeholder="输入值" />
      </Form.Item>
    );
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

export default TaskFilter;