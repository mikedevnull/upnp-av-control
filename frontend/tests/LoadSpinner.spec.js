import { mount } from '@vue/test-utils'
import LoadSpinner from '@/components/LoadSpinner.vue'


describe('LoadSpinner.vue', () => {
  it('renders correctly', () => {
    const wrapper = mount(LoadSpinner);
    expect(wrapper.element).toMatchSnapshot();
    wrapper.destroy();
  })
})
