import mockedAxios from 'axios';
import upnpapi from '@/upnpapi';


describe('upnpapi', () => {
  beforeEach(() => {
    mockedAxios.get.mockReset();
    mockedAxios.put.mockReset();
  })

  it('should query the API for a list of media renderers', async () => {
    // NOTE: current backend implementation still returns an 
    // object with a data attribute. This has been removed from the other endpoints
    // and will be changed here, too, when the renderer specific endpoints 
    // will be finished
    const backendResponse = { data: [{ name: 'foo', udn: '1234' }] }
    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValueOnce(axiosResponse);

    let renderers = await upnpapi.getMediaRenderers();
    expect(renderers.length).toBe(1);
    expect(mockedAxios.get).toHaveBeenCalledTimes(1);
    expect(mockedAxios.get).toHaveBeenCalledWith('/player/devices');
  })

  it('should query the API for a list of media servers', async () => {
    const backendResponse = [{ name: 'var', udn: '1234' }]
    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValueOnce(axiosResponse);

    let devices = await upnpapi.getLibraryDevices();
    expect(devices.length).toBe(1);
    expect(mockedAxios.get).toHaveBeenCalledTimes(1);
    expect(mockedAxios.get).toHaveBeenCalledWith('/library/devices');
  })

  it('should query the API to select the active renderer', async () => {
    const requestedUdn = '1234-5678';

    mockedAxios.put.mockResolvedValueOnce();
    await upnpapi.setActiveRenderer(requestedUdn);
    expect(mockedAxios.put).toHaveBeenCalledTimes(1)
    expect(mockedAxios.put).toHaveBeenCalledWith('/player/device', { udn: requestedUdn });
  })

  it('should use the API to set the current volume', async () => {
    mockedAxios.put.mockResolvedValueOnce('some_data');
    let result = await upnpapi.setCurrentVolume(4);
    expect(result).toBe('some_data');
    expect(mockedAxios.put).toHaveBeenCalledTimes(1);
    expect(mockedAxios.put).toHaveBeenCalledWith('/player/volume', { volume_percent: 4 });
  })

  it('should query the API to get the current playback state', async () => {
    const backendResponse = { volume: 2 };

    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValueOnce(axiosResponse)
    let result = await upnpapi.getCurrentPlaybackInfo()
    expect(result).toEqual(backendResponse);
  })

  it('should query the API to browse the root element of a media server', async () => {
    const backendResponse = [{ title: 'foo' }]
    const requestUdn = '1234-5678'
    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValueOnce(axiosResponse);

    let elements = await upnpapi.browseServer(requestUdn);
    expect(elements.length).toBe(1);
    expect(mockedAxios.get).toHaveBeenCalledTimes(1);
    expect(mockedAxios.get).toHaveBeenCalledWith(`/library/${requestUdn}/browse`, { params: {} });
  })

  it('should query the API to browse a specific object of a media server', async () => {
    const backendResponse = [{ title: 'child-of-foo' }];
    const requestUdn = '1234-5678';
    const objectID = 'foo';
    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValueOnce(axiosResponse);

    let elements = await upnpapi.browseServer(requestUdn, objectID);
    expect(elements.length).toBe(1);
    expect(mockedAxios.get).toHaveBeenCalledTimes(1);
    expect(mockedAxios.get).toHaveBeenCalledWith(`/library/${requestUdn}/browse`, { params: { objectID } });
  })

  it('should query the API for metadata of an specific object', async () => {
    const backendResponse = { title: 'foo' };
    const axiosResponse = { data: backendResponse };
    mockedAxios.get.mockResolvedValue(axiosResponse);
    const requestUdn = '1234-5678';
    const objectID = 'foo';
    let metadata = await upnpapi.getObjectMetadata(requestUdn, objectID);
    expect(metadata).toEqual(backendResponse);
    expect(mockedAxios.get).toHaveBeenCalledTimes(1);
    expect(mockedAxios.get).toHaveBeenCalledWith(`/library/${requestUdn}/metadata`, { params: { objectID } });

    metadata = await upnpapi.getObjectMetadata(requestUdn);
    expect(metadata).toEqual(backendResponse);
    expect(mockedAxios.get).toHaveBeenCalledTimes(2);
    expect(mockedAxios.get).toHaveBeenLastCalledWith(`/library/${requestUdn}/metadata`, { params: {} });

  })
})
