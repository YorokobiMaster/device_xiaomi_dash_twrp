/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 3 --hash 74a538630d5d90f732f361a2313cbb69b09eb047 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/secureclock/aidl/android.hardware.security.secureclock_interface/1/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging/android/hardware/security/keymint/KeyCreationResult.cpp.d -h out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging -Nhardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3 hardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3/android/hardware/security/keymint/KeyCreationResult.aidl
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
#include <aidl/android/hardware/security/keymint/Certificate.h>
#include <aidl/android/hardware/security/keymint/KeyCharacteristics.h>
#ifdef BINDER_STABILITY_SUPPORT
#include <android/binder_stability.h>
#endif  // BINDER_STABILITY_SUPPORT

namespace aidl::android::hardware::security::keymint {
class Certificate;
class KeyCharacteristics;
}  // namespace aidl::android::hardware::security::keymint
namespace aidl {
namespace android {
namespace hardware {
namespace security {
namespace keymint {
class KeyCreationResult {
public:
  typedef std::false_type fixed_size;
  static const char* descriptor;

  std::vector<uint8_t> keyBlob;
  std::vector<::aidl::android::hardware::security::keymint::KeyCharacteristics> keyCharacteristics;
  std::vector<::aidl::android::hardware::security::keymint::Certificate> certificateChain;

  binder_status_t readFromParcel(const AParcel* parcel);
  binder_status_t writeToParcel(AParcel* parcel) const;

  inline bool operator==(const KeyCreationResult& _rhs) const {
    return std::tie(keyBlob, keyCharacteristics, certificateChain) == std::tie(_rhs.keyBlob, _rhs.keyCharacteristics, _rhs.certificateChain);
  }
  inline bool operator<(const KeyCreationResult& _rhs) const {
    return std::tie(keyBlob, keyCharacteristics, certificateChain) < std::tie(_rhs.keyBlob, _rhs.keyCharacteristics, _rhs.certificateChain);
  }
  inline bool operator!=(const KeyCreationResult& _rhs) const {
    return !(*this == _rhs);
  }
  inline bool operator>(const KeyCreationResult& _rhs) const {
    return _rhs < *this;
  }
  inline bool operator>=(const KeyCreationResult& _rhs) const {
    return !(*this < _rhs);
  }
  inline bool operator<=(const KeyCreationResult& _rhs) const {
    return !(_rhs < *this);
  }

  static const ::ndk::parcelable_stability_t _aidl_stability = ::ndk::STABILITY_VINTF;
  inline std::string toString() const {
    std::ostringstream _aidl_os;
    _aidl_os << "KeyCreationResult{";
    _aidl_os << "keyBlob: " << ::android::internal::ToString(keyBlob);
    _aidl_os << ", keyCharacteristics: " << ::android::internal::ToString(keyCharacteristics);
    _aidl_os << ", certificateChain: " << ::android::internal::ToString(certificateChain);
    _aidl_os << "}";
    return _aidl_os.str();
  }
};
}  // namespace keymint
}  // namespace security
}  // namespace hardware
}  // namespace android
}  // namespace aidl
