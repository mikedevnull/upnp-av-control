import { mount, RouterLinkStub, enableAutoDestroy } from '@vue/test-utils'
import TheAppBar from '@/components/TheAppBar.vue'

enableAutoDestroy(afterEach)

describe('TheAppBar.vue', () => {
  it('renders correctly', () => {
    const wrapper = mount(TheAppBar, { stubs: { RouterLink: RouterLinkStub } });
    expect(wrapper.element).toMatchSnapshot();
  })
})
