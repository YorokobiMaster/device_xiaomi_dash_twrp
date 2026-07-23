/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 1 --hash d877e8a1608a00fd9068bcd7e69ea480a7ea17f0 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint_interface/3/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging/android/hardware/gatekeeper/GatekeeperVerifyResponse.cpp.d -h out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging -Nhardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1 hardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1/android/hardware/gatekeeper/GatekeeperVerifyResponse.aidl
 */
#pragma once

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <android/binder_interface_utils.h>
#include <android/binder_parcelable_utils.h>
#include <android/binder_to_string.h>
#include <aidl/android/hardware/security/keymint/HardwareAuthToken.h>
#ifdef BINDER_STABILITY_SUPPORT
#include <android/binder_stability.h>
#endif  // BINDER_STABILITY_SUPPORT

namespace aidl::android::hardware::security::keymint {
class HardwareAuthToken;
}  // namespace aidl::android::hardware::security::keymint
namespace aidl {
namespace android {
namespace hardware {
namespace gatekeeper {
class GatekeeperVerifyResponse {
public:
  typedef std::false_type fixed_size;
  static const char* descriptor;

  int32_t statusCode = 0;
  int32_t timeoutMs = 0;
  ::aidl::android::hardware::security::keymint::HardwareAuthToken hardwareAuthToken;

  binder_status_t readFromParcel(const AParcel* parcel);
  binder_status_t writeToParcel(AParcel* parcel) const;

  inline bool operator==(const GatekeeperVerifyResponse& _rhs) const {
    return std::tie(statusCode, timeoutMs, hardwareAuthToken) == std::tie(_rhs.statusCode, _rhs.timeoutMs, _rhs.hardwareAuthToken);
  }
  inline bool operator<(const GatekeeperVerifyResponse& _rhs) const {
    return std::tie(statusCode, timeoutMs, hardwareAuthToken) < std::tie(_rhs.statusCode, _rhs.timeoutMs, _rhs.hardwareAuthToken);
  }
  inline bool operator!=(const GatekeeperVerifyResponse& _rhs) const {
    return !(*this == _rhs);
  }
  inline bool operator>(const GatekeeperVerifyResponse& _rhs) const {
    return _rhs < *this;
  }
  inline bool operator>=(const GatekeeperVerifyResponse& _rhs) const {
    return !(*this < _rhs);
  }
  inline bool operator<=(const GatekeeperVerifyResponse& _rhs) const {
    return !(_rhs < *this);
  }

  static const ::ndk::parcelable_stability_t _aidl_stability = ::ndk::STABILITY_VINTF;
  inline std::string toString() const {
    std::ostringstream _aidl_os;
    _aidl_os << "GatekeeperVerifyResponse{";
    _aidl_os << "statusCode: " << ::android::internal::ToString(statusCode);
    _aidl_os << ", timeoutMs: " << ::android::internal::ToString(timeoutMs);
    _aidl_os << ", hardwareAuthToken: " << ::android::internal::ToString(hardwareAuthToken);
    _aidl_os << "}";
    return _aidl_os.str();
  }
};
}  // namespace gatekeeper
}  // namespace hardware
}  // namespace android
}  // namespace aidl
