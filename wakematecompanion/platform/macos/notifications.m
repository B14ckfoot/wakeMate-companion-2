// notifications.m
#import "notifications.h"
#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>
#import <UserNotifications/UserNotifications.h>

@interface Notifications : NSObject
+ (BOOL)showNotificationWithTitle:(NSString *)title message:(NSString *)message iconPath:(NSString *)iconPath;
@end

@implementation Notifications

+ (BOOL)showNotificationWithTitle:(NSString *)title message:(NSString *)message iconPath:(NSString *)iconPath {
    @autoreleasepool {
        // Check if UserNotifications framework is available (macOS 10.14+)
        if (NSClassFromString(@"UNUserNotificationCenter")) {
            UNUserNotificationCenter *center = [UNUserNotificationCenter currentNotificationCenter];
            
            // Request authorization
            [center requestAuthorizationWithOptions:(UNAuthorizationOptionAlert | UNAuthorizationOptionSound)
                                 completionHandler:^(BOOL granted, NSError * _Nullable error) {
                if (!granted) {
                    NSLog(@"Notification permission not granted");
                }
            }];
            
            // Create notification content
            UNMutableNotificationContent *content = [[UNMutableNotificationContent alloc] init];
            content.title = title;
            content.body = message;
            content.sound = [UNNotificationSound defaultSound];
            
            // Create unique identifier
            NSString *identifier = [NSString stringWithFormat:@"wakemate-%@", [[NSUUID UUID] UUIDString]];
            
            // Create request
            UNNotificationRequest *request = [UNNotificationRequest requestWithIdentifier:identifier
                                                                                  content:content
                                                                                  trigger:nil];
            
            // Add request to notification center
            [center addNotificationRequest:request withCompletionHandler:^(NSError * _Nullable error) {
                if (error) {
                    NSLog(@"Error showing notification: %@", error);
                }
            }];
            
            return YES;
        }
        // Fallback to NSUserNotification (deprecated but works on older macOS)
        else if (NSClassFromString(@"NSUserNotification")) {
            NSUserNotification *notification = [[NSUserNotification alloc] init];
            notification.title = title;
            notification.informativeText = message;
            notification.soundName = NSUserNotificationDefaultSoundName;
            
            if (iconPath != nil) {
                NSImage *icon = [[NSImage alloc] initWithContentsOfFile:iconPath];
                if (icon != nil) {
                    notification.contentImage = icon;
                }
            }
            
            [[NSUserNotificationCenter defaultUserNotificationCenter] deliverNotification:notification];
            return YES;
        }
        
        return NO;
    }
}

@end

int show_notification(const char *title, const char *message, const char *icon_path) {
    @autoreleasepool {
        NSString *titleStr = [NSString stringWithUTF8String:title];
        NSString *messageStr = [NSString stringWithUTF8String:message];
        NSString *iconPathStr = icon_path ? [NSString stringWithUTF8String:icon_path] : nil;
        
        BOOL result = [Notifications showNotificationWithTitle:titleStr message:messageStr iconPath:iconPathStr];
        return result ? 1 : 0;
    }
}