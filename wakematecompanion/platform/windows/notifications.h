// notifications.h
#ifndef WM_NOTIFICATIONS_H
#define WM_NOTIFICATIONS_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#define WM_EXPORT __declspec(dllexport)
#else
#define WM_EXPORT
#endif

// Show a Windows toast notification
// Returns TRUE if the notification was shown successfully, FALSE otherwise
WM_EXPORT BOOL show_notification(const char* title, const char* message, const char* icon_path);

#ifdef __cplusplus
}
#endif

#endif // WM_NOTIFICATIONS_H