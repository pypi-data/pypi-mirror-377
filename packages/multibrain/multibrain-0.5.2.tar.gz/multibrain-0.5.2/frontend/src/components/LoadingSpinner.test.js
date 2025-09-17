import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import LoadingSpinner from './LoadingSpinner.svelte';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(LoadingSpinner);
    
    const spinner = screen.getByRole('img', { hidden: true });
    expect(spinner).toBeInTheDocument();
    
    // Check default size (medium)
    expect(spinner).toHaveClass('w-8', 'h-8');
    
    // Check default color (blue)
    expect(spinner).toHaveClass('text-blue-500');
  });

  it('renders with custom size', () => {
    render(LoadingSpinner, { props: { size: 'small' } });
    
    const spinner = screen.getByRole('img', { hidden: true });
    expect(spinner).toHaveClass('w-4', 'h-4');
  });

  it('renders with custom color', () => {
    render(LoadingSpinner, { props: { color: 'white' } });
    
    const spinner = screen.getByRole('img', { hidden: true });
    expect(spinner).toHaveClass('text-white');
  });

  it('applies animation class', () => {
    render(LoadingSpinner);
    
    const spinner = screen.getByRole('img', { hidden: true });
    expect(spinner).toHaveClass('animate-spin');
  });

  it('renders all size variants correctly', () => {
    const sizes = ['small', 'medium', 'large'];
    const expectedClasses = {
      small: ['w-4', 'h-4'],
      medium: ['w-8', 'h-8'],
      large: ['w-12', 'h-12']
    };

    sizes.forEach(size => {
      const { unmount } = render(LoadingSpinner, { props: { size } });
      const spinner = screen.getByRole('img', { hidden: true });
      
      expectedClasses[size].forEach(className => {
        expect(spinner).toHaveClass(className);
      });
      
      unmount();
    });
  });

  it('renders all color variants correctly', () => {
    const colors = ['blue', 'gray', 'white'];
    const expectedClasses = {
      blue: 'text-blue-500',
      gray: 'text-gray-500',
      white: 'text-white'
    };

    colors.forEach(color => {
      const { unmount } = render(LoadingSpinner, { props: { color } });
      const spinner = screen.getByRole('img', { hidden: true });
      
      expect(spinner).toHaveClass(expectedClasses[color]);
      
      unmount();
    });
  });

  // Test for Svelte 5 migration
  it('works with $props() after migration', () => {
    // This test verifies the component works correctly after Svelte 5 migration
    const { container } = render(LoadingSpinner, { 
      props: { 
        size: 'large', 
        color: 'gray' 
      } 
    });
    
    const spinner = container.querySelector('svg');
    expect(spinner).toHaveClass('w-12', 'h-12', 'text-gray-500');
  });
});