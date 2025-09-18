import unittest

class TestImport(unittest.TestCase):
    def test_package_imports(self):
        import speexaec
        self.assertTrue(hasattr(speexaec, '__version__'))

    def test_utils(self):
        from speexaec import get_frame_size, get_filter_length
        # Typical telephony frame sizes
        self.assertEqual(get_frame_size(16000, 20), 320)
        self.assertEqual(get_frame_size(48000, 10), 480)
        # Filter length conversion
        self.assertEqual(get_filter_length(16000, 200), 3200)
        self.assertEqual(get_filter_length(48000, 100), 4800)

class TestCompiledExtension(unittest.TestCase):
    @unittest.skip("Optional: run only when the compiled extension is available")
    def test_compiled_classes_exist(self):
        # This test is skipped by default so CI without the native deps still passes.
        import importlib
        mod = importlib.import_module('speexaec')
        for name in ("EchoCanceller", "AudioPreprocessor", "AudioResampler"):
            # Check attributes exist when extension is built
            self.assertTrue(hasattr(mod, name))


if __name__ == '__main__':
    unittest.main(verbosity=2)
