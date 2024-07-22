'use client'
import React from 'react';

const CustomInput = ({ inputType, label, value, onChange, disabled }) => {
  return (
    <div className="mb-4">
    <label className="block text-gray-700 text-sm font-bold mb-2">{label}</label>
    <input
      type={inputType}
      value={value}
      onChange={onChange}
      disabled={disabled}
      className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${disabled ? 'bg-gray-100' : 'bg-white'}`}
    />
  </div>
  );
};

export default CustomInput;
