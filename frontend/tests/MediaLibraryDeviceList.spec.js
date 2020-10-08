import { shallowMount, createLocalVue, RouterLinkStub } from '@vue/test-utils'
import MediaLibraryDeviceList from '@/components/MediaLibraryDeviceList.vue'
import Vuex from 'vuex'

const localVue = createLocalVue()
localVue.use(Vuex)


describe('MediaLibraryDeviceList.vue', () => {
  let state;
  let store;

  beforeEach(() => {
    state = {
      available_servers: [{ friendly_name: 'FooServer', udn: '1234-5678' }, { friendly_name: 'BarServer', udn: 'abcd' }],
    }
    store = new Vuex.Store({ state });
  })


  it('renders links for each item in props.items', () => {
    const wrapper = shallowMount(MediaLibraryDeviceList, { store, localVue, stubs: { RouterLink: RouterLinkStub } });
    const links = wrapper.findAll(RouterLinkStub)
    expect(links).toHaveLength(2);

    const routeTarget0 = { name: 'browse', params: { udn: '1234-5678' } }
    expect(links.at(0).text()).toBe('FooServer');
    expect(links.at(0).props().to).toStrictEqual(routeTarget0);

    const routeTarget1 = { name: 'browse', params: { udn: 'abcd' } }
    expect(links.at(1).text()).toBe('BarServer');
    expect(links.at(1).props().to).toStrictEqual(routeTarget1);

  })
})
