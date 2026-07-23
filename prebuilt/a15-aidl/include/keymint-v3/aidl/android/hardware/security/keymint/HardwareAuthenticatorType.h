/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 3 --hash 74a538630d5d90f732f361a2313cbb69b09eb047 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/secureclock/aidl/android.hardware.security.secureclock_interface/1/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging/android/hardware/security/keymint/HardwareAuthenticatorType.cpp.d -h out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging -Nhardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3 hardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3/android/hardware/security/keymint/HardwareAuthenticatorType.aidl
 */
#pragma once

#include <array>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <android/binder_enums.h>
#ifdef BINDER_STABILITY_SUPPORT
#include <android/binder_stability.h>
#endif  // BINDER_STABILITY_SUPPORT

namespace aidl {
namespace android {
namespace hardware {
namespace security {
namespace keymint {
enum class HardwareAuthenticatorType : int32_t {
  NONE = 0,
  PASSWORD = 1,
  FINGERPRINT = 2,
  ANY = -1,
};

}  // namespace keymint
}  // namespace security
}  // namespace hardware
}  // namespace android
}  // namespace aidl
namespace aidl {
namespace android {
namespace hardware {
namespace security {
namespace keymint {
[[nodiscard]] static inline std::string toString(HardwareAuthenticatorType val) {
  switch(val) {
  case HardwareAuthenticatorType::NONE:
    return "NONE";
  case HardwareAuthenticatorType::PASSWORD:
    return "PASSWORD";
  case HardwareAuthenticatorType::FINGERPRINT:
    return "FINGERPRINT";
  case HardwareAuthenticatorType::ANY:
    return "ANY";
  default:
    return std::to_string(static_cast<int32_t>(val));
  }
}
}  // namespace keymint
}  // namespace security
}  // namespace hardware
}  // namespace android
}  // namespace aidl
namespace ndk {
namespace internal {
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wc++17-extensions"
template <>
constexpr inline std::array<aidl::android::hardware::security::keymint::HardwareAuthenticatorType, 4> enum_values<aidl::android::hardware::security::keymint::HardwareAuthenticatorType> = {
  aidl::android::hardware::security::keymint::HardwareAuthenticatorType::NONE,
  aidl::android::hardware::security::keymint::HardwareAuthenticatorType::PASSWORD,
  aidl::android::hardware::security::keymint::HardwareAuthenticatorType::FINGERPRINT,
  aidl::android::hardware::security::keymint::HardwareAuthenticatorType::ANY,
};
#pragma clang diagnostic pop
}  // namespace internal
}  // namespace ndk
