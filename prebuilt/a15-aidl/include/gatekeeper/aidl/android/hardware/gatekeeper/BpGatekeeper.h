/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 1 --hash d877e8a1608a00fd9068bcd7e69ea480a7ea17f0 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint_interface/3/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging/android/hardware/gatekeeper/IGatekeeper.cpp.d -h out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging -Nhardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1 hardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1/android/hardware/gatekeeper/IGatekeeper.aidl
 */
#pragma once

#include "aidl/android/hardware/gatekeeper/IGatekeeper.h"

#include <android/binder_ibinder.h>

namespace aidl {
namespace android {
namespace hardware {
namespace gatekeeper {
class BpGatekeeper : public ::ndk::BpCInterface<IGatekeeper> {
public:
  explicit BpGatekeeper(const ::ndk::SpAIBinder& binder);
  virtual ~BpGatekeeper();

  ::ndk::ScopedAStatus deleteAllUsers() override;
  ::ndk::ScopedAStatus deleteUser(int32_t in_uid) override;
  ::ndk::ScopedAStatus enroll(int32_t in_uid, const std::vector<uint8_t>& in_currentPasswordHandle, const std::vector<uint8_t>& in_currentPassword, const std::vector<uint8_t>& in_desiredPassword, ::aidl::android::hardware::gatekeeper::GatekeeperEnrollResponse* _aidl_return) override;
  ::ndk::ScopedAStatus verify(int32_t in_uid, int64_t in_challenge, const std::vector<uint8_t>& in_enrolledPasswordHandle, const std::vector<uint8_t>& in_providedPassword, ::aidl::android::hardware::gatekeeper::GatekeeperVerifyResponse* _aidl_return) override;
  ::ndk::ScopedAStatus getInterfaceVersion(int32_t* _aidl_return) override;
  ::ndk::ScopedAStatus getInterfaceHash(std::string* _aidl_return) override;
  int32_t _aidl_cached_version = -1;
  std::string _aidl_cached_hash = "-1";
  std::mutex _aidl_cached_hash_mutex;
};
}  // namespace gatekeeper
}  // namespace hardware
}  // namespace android
}  // namespace aidl
