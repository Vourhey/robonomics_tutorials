#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ROS
import rospy

# Robonomics communication
from robonomics_msgs.msg import Offer, Demand
from ethereum_common.msg import Address, UInt256
from ethereum_common.srv import Accounts, BlockNumber
from ipfs_common.msg import Multihash


class TraderNode:

    def __init__(self):
        rospy.init_node('trader_node')
        rospy.loginfo('Launching trader node...')

        self.MODEL = rospy.get_param("~model")      # Unique identifier for the agent

        rospy.wait_for_service('/eth/current_block')
        rospy.wait_for_service('/eth/accounts')
        self.accounts = rospy.ServiceProxy('/eth/accounts', Accounts)()
        rospy.loginfo(str(self.accounts))  # AIRA ethereum addresses

        self.signing_offer = rospy.Publisher('/liability/infochan/eth/signing/offer', Offer, queue_size=128)

        rospy.Subscriber('/liability/infochan/incoming/demand', Demand, self.on_incoming_demand)

        rospy.loginfo('Trader node is launched')

    def on_incoming_demand(self, incoming: Demand):
        rospy.loginfo('Incoming demand %s...', str(incoming))
        if incoming.model.multihash == self.MODEL:
            rospy.loginfo('For my model and token!')

            self.make_offer(incoming)
        else:
            rospy.loginfo('Doesn\'t fit my model or token, skip it')

    def make_deadline(self):
        lifetime = 100      # how many blocks the offer is valid since the current block
        deadline = rospy.ServiceProxy('/eth/current_block', BlockNumber)().number + lifetime
        return str(deadline)

    def make_offer(self, demand: Demand):
        rospy.loginfo('Making offer...')

        offer = Offer()
        offer.model = Multihash(self.MODEL)
        offer.objective = demand.objective
        offer.token = demand.token
        offer.cost = demand.cost
        offer.lighthouse = demand.lighthouse
        offer.validator = demand.validator
        offer.lighthouseFee = UInt256("0")
        offer.deadline = UInt256()
        offer.deadline.uint256 = self.make_deadline()

        self.signing_offer.publish(offer)
        rospy.loginfo(offer)

    def spin(self):
        rospy.spin()


if __name__ == '__main__':
    TraderNode().spin()

