//
//  main.swift
//  adhocnet
//
//  Created by Joe Hildebrand on 11/14/15.
//  Copyright © 2015 Joe Hildebrand. All rights reserved.
//
//  Based on the discussion at:
//  http://stackoverflow.com/questions/31342348/programmatically-create-ad-hoc-network-os-x
//
import Foundation
import CoreWLAN

let args = CommandLine.arguments
if args.count < 3 {
    let p = args[0].components(separatedBy: "/")

    print("Usage: \(p.last!) <SSID> <Password>")
    exit(64)
}
let networkName = args[1]
let password = args[2]


if let iface = CWWiFiClient.shared().interface() {
    do {
        try iface.startIBSSMode(
            withSSID: networkName.data(using: String.Encoding.utf8)!,
            security: CWIBSSModeSecurity.WEP104,
            channel: 11,
            password: password as String)
        print("Success")
    } catch let error as NSError {
        print("Error", error)
        exit(1)
    }
} else {
    print("Invalid interface")
    exit(1)
}
