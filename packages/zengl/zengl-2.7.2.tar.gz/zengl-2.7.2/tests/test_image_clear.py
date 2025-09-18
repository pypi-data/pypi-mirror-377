import numpy as np
import zengl


def test_image_clear(ctx: zengl.Context):
    img = ctx.image((4, 4), 'rgba8unorm', b'test' * 16)
    assert img.read() == b'test' * 16
    img.clear_value = (0.0, 0.0, 0.0, 1.0)
    img.clear()
    assert img.read() == b'\x00\x00\x00\xff' * 16


def test_image_clear_floats(ctx: zengl.Context):
    img = ctx.image((4, 4), 'rg32float', np.zeros((4, 4, 2), 'f4'))
    content = np.frombuffer(img.read(), 'f4').reshape(4, 4, 2)
    expected = np.zeros((4, 4, 2), 'f4')
    np.testing.assert_array_almost_equal(content, expected, 2)
    img.clear_value = (0.25, 0.75)
    img.clear()
    content = np.frombuffer(img.read(), 'f4').reshape(4, 4, 2)
    expected = np.full((4, 4, 2), (0.25, 0.75), 'f4')
    np.testing.assert_array_almost_equal(content, expected, 2)


def test_image_clear_integers(ctx: zengl.Context):
    img = ctx.image((4, 4), 'rgba32sint', np.zeros((4, 4, 4), 'i4'))
    content = np.frombuffer(img.read(), 'i4').reshape(4, 4, 4)
    expected = np.zeros((4, 4, 4), 'i4')
    np.testing.assert_array_equal(content, expected)
    img.clear_value = (-100, -55, 99, 1048576)
    img.clear()
    content = np.frombuffer(img.read(), 'i4').reshape(4, 4, 4)
    expected = np.full((4, 4, 4), (-100, -55, 99, 1048576), 'i4')
    np.testing.assert_array_equal(content, expected)


def test_invalid_image_clear_cubemap(ctx: zengl.Context):
    img = ctx.image((16, 16), 'rgba8unorm', cubemap=True)
    img.clear_value = (1.0, 0.0, 0.0, 1.0)
    img.clear()
    assert img.face(0).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(1).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(2).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(3).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(4).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(5).read() == b'\xff\x00\x00\xff' * 256
    assert img.read() == b'\xff\x00\x00\xff' * 256 * 6


def test_invalid_image_clear_array(ctx: zengl.Context):
    img = ctx.image((16, 16), 'rgba8unorm', array=4)
    img.clear_value = (1.0, 0.0, 0.0, 1.0)
    img.clear()
    assert img.face(0).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(1).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(2).read() == b'\xff\x00\x00\xff' * 256
    assert img.face(3).read() == b'\xff\x00\x00\xff' * 256
    assert img.read() == b'\xff\x00\x00\xff' * 256 * 4
