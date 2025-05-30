// notifications.cpp
#include "notifications.h"
#include <Windows.h>
#include <string>
#include <iostream>

// Add the WinToast header
// You need to download WinToast from: https://github.com/mohabouje/WinToast
#include "wintoast/wintoast.h"
using namespace WinToastLib;

class WinToastHandler : public IWinToastHandler {
public:
    void toastActivated() const override {}
    void toastActivated(int actionIndex) const override {}
    void toastDismissed(WinToastDismissalReason state) const override {}
    void toastFailed() const override {}
};

// Convert a UTF-8 string to a wide string
std::wstring utf8_to_wide(const char* utf8_str) {
    if (!utf8_str) return std::wstring();
    
    int size_needed = MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, NULL, 0);
    std::wstring wstr(size_needed, 0);
    MultiByteToWideChar(CP_UTF8, 0, utf8_str, -1, &wstr[0], size_needed);
    
    // Remove the null terminator if added
    if (!wstr.empty() && wstr.back() == L'\0') {
        wstr.pop_back();
    }
    
    return wstr;
}

extern "C" {
    __declspec(dllexport) BOOL show_notification(const char* title, const char* message, const char* icon_path) {
        try {
            // Initialize WinToast
            WinToast::instance()->setAppName(L"WakeMATECompanion");
            const auto aumi = WinToast::configureAUMI(L"WakeMATECompanion", L"WakeMATECompanion", L"", L"");
            WinToast::instance()->setAppUserModelId(aumi);
            
            if (!WinToast::instance()->initialize()) {
                std::cerr << "Failed to initialize WinToast" << std::endl;
                return FALSE;
            }
            
            // Convert strings to wide strings
            std::wstring wide_title = utf8_to_wide(title);
            std::wstring wide_message = utf8_to_wide(message);
            std::wstring wide_icon_path;
            if (icon_path) {
                wide_icon_path = utf8_to_wide(icon_path);
            }
            
            // Create toast
            WinToastTemplate templ = WinToastTemplate(WinToastTemplate::ImageAndText02);
            templ.setTextField(wide_title, WinToastTemplate::FirstLine);
            templ.setTextField(wide_message, WinToastTemplate::SecondLine);
            
            if (!wide_icon_path.empty()) {
                templ.setImagePath(wide_icon_path);
            }
            
            // Show toast
            WinToastHandler* handler = new WinToastHandler();
            int64_t toast_id = WinToast::instance()->showToast(templ, handler);
            
            return toast_id >= 0 ? TRUE : FALSE;
        }
        catch (const std::exception& e) {
            std::cerr << "Exception in show_notification: " << e.what() << std::endl;
            return FALSE;
        }
        catch (...) {
            std::cerr << "Unknown exception in show_notification" << std::endl;
            return FALSE;
        }
    }
}