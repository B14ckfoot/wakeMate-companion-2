// notifications.h
#ifndef WM_NOTIFICATIONS_H
#define WM_NOTIFICATIONS_H

#ifdef __cplusplus
extern "C" {
#endif

// Show a macOS notification
// Returns TRUE (1) if the notification was shown successfully, FALSE (0) otherwise
int show_notification(const char *title, const char *message, const char *icon_path);

#ifdef __cplusplus
}
#endif

#endif // WM_NOTIFICATIONS_H