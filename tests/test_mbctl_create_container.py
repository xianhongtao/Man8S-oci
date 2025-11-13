import unittest
from mbctl.exec.create_nspawn_container_from_oci_url import pull_oci_image_and_create_container


class TestPullOciImage(unittest.TestCase):
    def test_pull_oci_image_and_create_container(self):
        pull_oci_image_and_create_container(
            oci_image_url="ghcr.nju.edu.cn/bitwarden/self-host:latest",
            container_name="TestBWContainer1",
            container_template="netns-init",
            provided_mount_configs={
                "/etc/bitwarden": "/var/lib/man8machine_storage/TestBWContainer1/etc/bitwarden"
            }
        )


if __name__ == "__main__":
    unittest.main()